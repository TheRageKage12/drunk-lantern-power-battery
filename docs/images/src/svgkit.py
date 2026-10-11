"""Tiny helpers for hand-built schematic SVGs (no external deps)."""

RED, ORANGE, BLACK, GREEN, GREY = "#d62828", "#f77f00", "#222222", "#2a9d2a", "#777777"
INK = "#222222"
FONT = "font-family=\"Helvetica, Arial, sans-serif\""


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="Helvetica, Arial, sans-serif" font-size="12" fill="{INK}">',
            f"<title>{title}</title>",
            "<defs>",
            '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker>',
            "</defs>",
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        ]
        # per-colour markers (context-stroke is not supported everywhere)
        for name, col in (("arrR", RED), ("arrO", ORANGE), ("arrK", BLACK), ("arrG", GREEN),
                          ("arrGy", GREY), ("arrB", "#1d4ed8"), ("arrP", "#7c3aed")):
            self.parts.insert(4, f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                                 f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')

    def add(self, s):
        self.parts.append(s)

    # ------------------------------------------------------------ primitives
    def text(self, x, y, s, size=12, anchor="start", weight="normal", color=INK, italic=False, family=None):
        st = ' font-style="italic"' if italic else ""
        fam = f' font-family="{family}"' if family else ""
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" '
                 f'fill="{color}"{st}{fam}>{esc(s)}</text>')

    def lines(self, x, y, rows, size=12, anchor="start", color=INK, lh=None, weight="normal"):
        lh = lh or round(size * 1.3)
        for i, r in enumerate(rows):
            self.text(x, y + i * lh, r, size=size, anchor=anchor, color=color, weight=weight)

    def rect(self, x, y, w, h, fill="#ffffff", stroke=INK, sw=1.2, rx=0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, fill="#ffffff", stroke=INK, sw=1.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def path(self, d, stroke=INK, sw=1.2, fill="none", dash=None, marker=None, cap="round", opacity=None):
        m = f' marker-end="url(#{marker})"' if marker else ""
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}" '
                 f'stroke-linejoin="round"{ds}{m}{op}/>')

    def wire(self, pts, color=INK, sw=2, marker=None, dash=None):
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        self.path(d, stroke=color, sw=sw, marker=marker, dash=dash)

    def dot(self, x, y, color=INK, r=3.2):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')

    def gnd(self, x, y, color=BLACK, size=1.0):
        """ground symbol whose top touches (x, y), pointing down"""
        w = 16 * size
        self.path(f"M{x - w/2},{y} L{x + w/2},{y} M{x - w*0.33},{y + 5*size} L{x + w*0.33},{y + 5*size} "
                  f"M{x - w*0.12},{y + 10*size} L{x + w*0.12},{y + 10*size}", stroke=color, sw=2)

    def res_h(self, x1, x2, y, label, color=GREEN, lab_dy=-8, size=10):
        """horizontal resistor between x1 and x2 (body 40 wide centred)"""
        cx = (x1 + x2) / 2
        self.wire([(x1, y), (cx - 20, y)], color)
        self.wire([(cx + 20, y), (x2, y)], color)
        self.rect(cx - 20, y - 6, 40, 12, fill="#ffffff", stroke=INK, sw=1.4)
        self.text(cx, y + lab_dy, label, size=size, anchor="middle")

    def res_v(self, x, y1, y2, label, color=GREEN, lab_dx=10, size=10):
        cy = (y1 + y2) / 2
        self.wire([(x, y1), (x, cy - 20)], color)
        self.wire([(x, cy + 20), (x, y2)], color)
        self.rect(x - 6, cy - 20, 12, 40, fill="#ffffff", stroke=INK, sw=1.4)
        self.text(x + lab_dx, cy + 4, label, size=size, anchor="start")

    def pin(self, x, y, color=INK, r=3):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" stroke="{color}" stroke-width="1.5"/>')

    def arrow(self, pts, color=INK, sw=1.5, dash=None):
        m = {RED: "arrR", ORANGE: "arrO", BLACK: "arrK", GREEN: "arrG", GREY: "arrGy", INK: "arrK",
             "#1d4ed8": "arrB", "#7c3aed": "arrP"}.get(color, "arrK")
        self.wire(pts, color, sw=sw, marker=m, dash=dash)

    def finish(self):
        self.parts.append("</svg>")
        return "\n".join(self.parts) + "\n"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
