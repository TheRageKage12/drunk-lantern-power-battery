"""Make docs/videos/*.mp4 from the 3D assembly viewer (docs/assembly-viewer/index.html).

    cd cad && python3 export_viewer.py && python3 make_videos.py [guide] [explode] [service]

  assembly-guide.mp4         one titled chapter per build step (the viewer's STEPS, same numbers as the build guide)
  separate-and-assemble.mp4  the whole lantern spreading apart and going back together
  service-access.mp4         what opens for service: lid off, lantern off the cartridge and the bag out, bells off

The page is driven with Playwright (headless Chromium, software WebGL) through its window.viewer hooks on a manual
clock, so every run gives the same frames. Frames are encoded with ffmpeg (H.264, yuv420p, faststart, 1280 x 720).
Needs: python3 -m pip install playwright; Chromium (set CHROMIUM=/path/to/chrome if Playwright's own is missing);
ffmpeg on the PATH. Takes a few minutes.
"""
import os, sys, math, shutil, subprocess, tempfile
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, '..', 'docs', 'assembly-viewer', 'index.html')
OUT = os.path.join(HERE, '..', 'docs', 'videos')
W, H, FPS = 1280, 720, 25
DT = 1000 / FPS

# overlay for the videos: the viewer's own side panel and buttons are hidden and replaced by a title, captions and a
# progress bar in the same fonts and colours
CSS = """
:root { color-scheme: light; }
.stage-top, .stage-bottom, .pick, .loading { display: none !important; }
#vid-head { position: absolute; top: 22px; left: 28px; right: 28px; pointer-events: none; z-index: 5; }
#vid-head .kick { font: 600 13px var(--f-body); letter-spacing: .1em; text-transform: uppercase; color: var(--accent); }
#vid-head h1 { font: 700 34px/1.05 var(--f-display); margin: 4px 0 0; color: var(--ink); text-transform: uppercase; letter-spacing: .02em; }
#vid-cap { position: absolute; left: 28px; right: 28px; bottom: 26px; font: 500 21px/1.35 var(--f-body); color: var(--ink);
  z-index: 5; max-width: 980px; background: color-mix(in srgb, var(--stage) 85%, transparent); padding: 8px 12px; border-radius: 8px; }
#vid-cap:empty { display: none; }
#vid-side { position: absolute; top: 0; right: 0; bottom: 0; width: 430px; box-sizing: border-box; padding: 30px 30px 26px;
  background: var(--panel); border-left: 1px solid var(--line); display: flex; flex-direction: column; gap: 10px; z-index: 5; }
#vid-side .count { font: 600 13px var(--f-mono); color: var(--muted); letter-spacing: .06em; text-transform: uppercase; }
#vid-side .stage { font: 600 13px var(--f-body); color: var(--accent); letter-spacing: .1em; text-transform: uppercase; margin-top: 6px; }
#vid-side h2 { font: 600 38px/1.02 var(--f-display); margin: 0; color: var(--ink); text-wrap: balance; }
#vid-side ol { margin: 6px 0 0; padding-left: 22px; display: grid; gap: 9px; font: 17px/1.4 var(--f-body); color: var(--ink); }
#vid-side .hw { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
#vid-side .hw span { font: 13px var(--f-mono); background: var(--chip); border-radius: 4px; padding: 3px 7px; }
#vid-side .foot { margin-top: auto; font: 13px var(--f-body); color: var(--muted); }
#vid-bar { position: absolute; left: 0; right: 0; bottom: 0; height: 6px; background: var(--line); z-index: 6; }
#vid-bar i { display: block; height: 100%; width: 0; background: var(--accent); }
"""

JS_SETUP = """([css, side]) => {
  const st = document.createElement('style'); st.textContent = css; document.head.append(st);
  document.querySelector('.panel').style.display = 'none';
  document.querySelector('.app').style.gridTemplateColumns = side ? 'minmax(0,1fr) 430px' : 'minmax(0,1fr)';
  const stage = document.querySelector('.stage');
  const head = document.createElement('div'); head.id = 'vid-head'; head.innerHTML = '<div class="kick"></div><h1></h1>'; stage.append(head);
  const cap = document.createElement('div'); cap.id = 'vid-cap'; stage.append(cap);
  const bar = document.createElement('div'); bar.id = 'vid-bar'; bar.innerHTML = '<i></i>'; document.body.append(bar);
  if (side) { const s = document.createElement('div'); s.id = 'vid-side'; document.body.append(s); }
  window.dispatchEvent(new Event('resize'));
}"""

JS_TEXT = """([kick, title, cap, prog]) => {
  document.querySelector('#vid-head .kick').textContent = kick;
  document.querySelector('#vid-head h1').textContent = title;
  document.getElementById('vid-cap').textContent = cap;
  document.querySelector('#vid-bar i').style.width = (prog * 100).toFixed(2) + '%';
}"""

JS_SIDE = """([s, total]) => {
  const el = document.getElementById('vid-side'); el.innerHTML = '';
  const add = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; el.append(e); return e; };
  add('div', 'count', `Step ${String(s.n).padStart(2, '0')} / ${total}`);
  add('div', 'stage', s.stage);
  add('h2', '', s.title);
  const ol = add('ol'); s.body.forEach(t => { const li = document.createElement('li'); li.textContent = t; ol.append(li); });
  if (s.hw.length) { const hw = add('div', 'hw'); s.hw.forEach(t => { const sp = document.createElement('span'); sp.textContent = t; hw.append(sp); }); }
  add('div', 'foot', `Build guide, step ${s.n}. Drag the model yourself in docs/assembly-viewer.`);
}"""


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


class Recorder:
    """Frames on disk plus how long each one shows; held frames are written once."""
    def __init__(self, page, d):
        self.page, self.d, self.items, self.t = page, d, [], 0.0

    def frame(self, hold=None):
        path = os.path.join(self.d, f'f{len(self.items):05d}.png')
        self.page.screenshot(path=path)
        dur = hold if hold is not None else 1 / FPS
        self.items.append((path, dur)); self.t += dur

    def run(self, seconds, each=None):
        """Advance the viewer clock frame by frame for `seconds`, calling each(t in 0..1) before every frame."""
        n = max(1, round(seconds * FPS))
        for i in range(n):
            if each: each((i + 1) / n)
            self.page.evaluate(f'viewer.tick({DT})')
            self.frame()

    def hold(self, seconds):
        if seconds > 0:
            self.page.evaluate(f'viewer.tick({DT})')
            self.frame(hold=seconds)

    def encode(self, out, title, chapters=None):
        lst = os.path.join(self.d, 'list.txt')
        with open(lst, 'w') as f:
            for p, dur in self.items:
                f.write(f"file '{p}'\nduration {dur:.4f}\n")
            f.write(f"file '{self.items[-1][0]}'\n")
        meta = os.path.join(self.d, 'meta.txt')
        with open(meta, 'w') as f:
            f.write(';FFMETADATA1\n' + f'title={esc(title)}\n')
            for start, end, name in chapters or []:
                f.write(f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(start * 1000)}\nEND={round(end * 1000)}\ntitle={esc(name)}\n')
        cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', meta,
               '-map', '0:v', '-map_metadata', '1', '-map_chapters', '1',
               '-vf', f'fps={FPS},scale={W}:{H}:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow',
               '-crf', '22', '-tune', 'animation', '-movflags', '+faststart', out]
        subprocess.run(cmd, check=True)
        print(f'{os.path.relpath(out)}: {self.t:.1f} s, {len(chapters or [])} chapters')


def esc(s):
    return ''.join('\\' + c if c in '=;#\\\n' else c for c in s)


def open_page(pw, side):
    exe = os.environ.get('CHROMIUM')
    if not exe and not os.path.exists(pw.chromium.executable_path) and os.path.exists('/opt/pw-browsers/chromium'):
        exe = '/opt/pw-browsers/chromium'
    b = pw.chromium.launch(executable_path=exe, args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1, color_scheme='light',
                    reduced_motion='no-preference')
    pg.goto('file://' + os.path.abspath(PAGE))
    pg.wait_for_function('window.viewer && window.viewer.ready', timeout=120000)
    pg.evaluate('document.fonts.ready')
    pg.evaluate(JS_SETUP, [CSS, side])
    pg.wait_for_timeout(300)
    pg.evaluate('viewer.manual(true)')
    return b, pg


def text(pg, kick, title, cap='', prog=0.0):
    pg.evaluate(JS_TEXT, [kick, title, cap, prog])


# ---------------------------------------------------------------- 1. step by step, one chapter per build step
def guide(pw, d):
    b, pg = open_page(pw, side=True)
    rec = Recorder(pg, d)
    steps = pg.evaluate('viewer.steps')
    total = steps[-1]['n']
    chapters = []
    for i, s in enumerate(steps):
        words = sum(len(t.split()) for t in s['body'])
        dur = min(9.0, max(6.0, 3.0 + words * 0.11))          # about 0.5-1 s of video per second of reading
        t0 = rec.t
        text(pg, 'Lantern · assembly guide · rev C', s['stage'], '', (i + 1) / len(steps))
        pg.evaluate(JS_SIDE, [s, total])
        pg.evaluate(f'viewer.go({i})')
        anim = 2.6
        rec.run(anim)                                          # parts fly in, camera moves
        rec.hold(dur - anim)
        chapters.append((t0, rec.t, f"{s['n']}. {s['title']}"))
    rec.encode(os.path.join(OUT, 'assembly-guide.mp4'), 'Lantern assembly guide', chapters)
    b.close()


# ---------------------------------------------------------------- 2. exploded assembly
def explode(pw, d):
    b, pg = open_page(pw, side=False)
    rec = Recorder(pg, d)
    kick, title = 'Lantern · rev C', 'Exploded assembly'
    pg.evaluate('viewer.mode("built")')
    pg.evaluate('viewer.spread(0)')
    # (end time s, caption, spread at the end of the segment); the spread eases between segments
    segs = [(1.5, 'Every printed part in its built position.', 0.0),
            (6.5, 'Top stack up, foot, drum and cartridge down, bells out front and back, handle up and out.', 1.0),
            (9.0, 'Top stack up, foot, drum and cartridge down, bells out front and back, handle up and out.', 1.0),
            (13.5, 'And back together.', 0.0),
            (15.0, 'And back together.', 0.0)]
    T, SPIN = segs[-1][0], 14.0                                # s, deg/s round the vertical axis

    def at(t):
        t0, k0 = 0.0, 0.0
        for t1, cap, k1 in segs:
            if t <= t1:
                return cap, k0 + (k1 - k0) * ease((t - t0) / (t1 - t0))
            t0, k0 = t1, k1
        return segs[-1][1], segs[-1][2]

    def each(u):
        t = u * T
        cap, k = at(t)
        a = math.radians(-37 + SPIN * t)                       # start from the audience side, front right
        d3 = [math.cos(a), math.sin(a), 0.3]
        pg.evaluate(f'viewer.spread({k:.4f})')
        pg.evaluate(f'viewer.view([{d3[0]:.4f}, {d3[1]:.4f}, {d3[2]}], null, {k:.4f}, {1.0 + 0.18 * k:.4f}); viewer.jump()')
        text(pg, kick, title, cap, u)
    rec.run(T, each)
    rec.encode(os.path.join(OUT, 'separate-and-assemble.mp4'), 'Lantern exploded assembly')
    b.close()


# ---------------------------------------------------------------- 3. opening for service
def service(pw, d):
    b, pg = open_page(pw, side=False)
    rec = Recorder(pg, d)
    g = pg.evaluate('viewer.groups')
    kick, title = 'Lantern · rev C', 'Opening for service'

    def offsets(*moves):
        m = {}
        for names, v in moves:
            for n in names:
                m[n] = [a + c for a, c in zip(m.get(n, [0, 0, 0]), v)]
        return m
    BUILT = {}
    LID_OFF = offsets((g['LID'], [0, 0, 120]))
    LIFT = offsets((g['LANTERN'], [0, 0, 250]))
    BAG_OUT = offsets((g['LANTERN'], [0, 0, 250]), (['bag_cover'], [-110, -70, 30]), (['bag_envelope'], [0, 0, 120]))
    BELLS = offsets((g['FRONT_BELL'], [0, -150, 0]), (g['REAR_BELL'], [0, 150, 0]))
    # frame the camera once round every pose so it holds still
    pg.evaluate('m => viewer.pose(m)', offsets((g['LANTERN'], [0, 0, 250]), (g['FRONT_BELL'], [0, -150, 0]),
                                               (g['REAR_BELL'], [0, 150, 0])))
    pg.evaluate('viewer.view([-0.75, -1, 0.3], null, 0, 1.12)'); pg.evaluate('viewer.jump()')   # front left: the bag side
    pg.evaluate('m => viewer.pose(m)', BUILT); rec.run(0.6)

    T = [0.0]
    total = 19.0

    def go(a, b2, secs, cap):
        def each(t):
            k = ease(t)
            m = {n: [x + (y - x) * k for x, y in zip(a.get(n, [0, 0, 0]), b2.get(n, [0, 0, 0]))] for n in set(a) | set(b2)}
            pg.evaluate('m => viewer.pose(m)', m)
            text(pg, kick, title, cap, (T[0] + t * secs) / total)
        rec.run(secs, each); T[0] += secs

    def stay(secs, cap):
        rec.run(secs, lambda t: text(pg, kick, title, cap, (T[0] + t * secs) / total)); T[0] += secs

    stay(1.0, 'Everything here comes apart by hand: twist locks and knurled thumbscrews.')
    c = 'Charge or power switch: twist the lid anticlockwise and lift it off. S1 and the charge socket are on the cap floor.'
    go(BUILT, LID_OFF, 1.5, c); stay(1.6, c); go(LID_OFF, BUILT, 1.0, c)
    c = 'Refill: twist the lantern a little anticlockwise and lift it off by the handle. The cartridge stays on the table.'
    go(BUILT, LIFT, 2.0, c); stay(0.6, c)
    c = 'Lift the bag cover and take the bag out by its spout. Fill it, put it back, clip the tube, cover on.'
    go(LIFT, BAG_OUT, 1.6, c); stay(1.2, c); go(BAG_OUT, LIFT, 1.2, c)
    c = 'Lantern back on the cartridge, twist clockwise to lock.'
    go(LIFT, BUILT, 1.6, c)
    c = 'Bells: 2 thumbscrews each from inside the sphere, then slide straight off (its LED lead has slack).'
    go(BUILT, BELLS, 1.6, c); stay(1.2, c); go(BELLS, BUILT, 1.3, c)
    stay(0.6, '')
    rec.encode(os.path.join(OUT, 'service-access.mp4'), 'Lantern opening for service')
    b.close()


if __name__ == '__main__':
    want = sys.argv[1:] or ['guide', 'explode', 'service']
    if not shutil.which('ffmpeg'):
        sys.exit('ffmpeg not found')
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as pw:
        for name in want:
            with tempfile.TemporaryDirectory() as d:
                {'guide': guide, 'explode': explode, 'service': service}[name](pw, d)
