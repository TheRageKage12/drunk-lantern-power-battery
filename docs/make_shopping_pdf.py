"""Render docs/SHOPPING_LIST.md to docs/SHOPPING_LIST.pdf (letter, tick boxes, clickable links).

    pip install markdown playwright     # Chromium: the preinstalled one, or `playwright install chromium`
    python3 docs/make_shopping_pdf.py
"""
import os, re, asyncio, markdown
HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = os.path.join(HERE, 'SHOPPING_LIST.md'), os.path.join(HERE, 'SHOPPING_LIST.pdf')
CHROME = os.environ.get('CHROME', '/opt/pw-browsers/chromium')

CSS = """
body { font: 10.5pt/1.35 Helvetica, Arial, sans-serif; color: #111; margin: 0; }
h1 { font-size: 17pt; margin: 0 0 4pt; } h2 { font-size: 12.5pt; margin: 12pt 0 4pt; border-bottom: 1px solid #999; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 6pt; } th, td { border: 1px solid #bbb; padding: 2.5pt 4pt; vertical-align: top; text-align: left; }
th { background: #eee; } td:first-child { width: 14pt; text-align: center; } a { color: #0645ad; text-decoration: none; }
.box { display: inline-block; width: 9pt; height: 9pt; border: 1.2px solid #333; vertical-align: middle; }
p, li { margin: 3pt 0; } ul { padding-left: 16pt; }
"""

def html():
    md = open(SRC, encoding='utf-8').read()
    md = md.replace('| [ ] |', '| <span class="box"></span> |').replace('- [ ] ', '- <span class="box"></span> ')
    body = markdown.markdown(md, extensions=['tables'])
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'

async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        kw = {'executable_path': CHROME} if os.path.exists(CHROME) else {}
        b = await p.chromium.launch(**kw)
        pg = await b.new_page()
        await pg.set_content(html())
        await pg.pdf(path=OUT, format='Letter', margin={'top': '14mm', 'bottom': '14mm', 'left': '14mm', 'right': '14mm'}, print_background=True)
        await b.close()
    print('wrote', OUT)

if __name__ == '__main__':
    asyncio.run(main())
