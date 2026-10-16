import pathlib, re, sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path('/tmp/claude-0/-home-claude/cedbf475-5c83-5947-b725-7f0d93a6350e/scratchpad')
SRC = ROOT / 'maquette/project'
OUT = ROOT / 'render'
harness = (OUT / 'harness.js').read_text()

def prep(name):
    html = (SRC / name).read_text()
    html = html.replace('<script src="./support.js"></script>', '')
    html = html.replace('</body>', '<script>' + harness + '</script></body>')
    html = html.replace('/_blob/d58a0ac035c394264bf474850f33072f', (ROOT / 'maquette/assets/anid-logo.svg').as_uri()).replace('/_blob/e7c52a49379b090417d28307896de81d', (ROOT / 'bio/fond-empreintes-clair-v2.svg').as_uri()).replace('/_blob/41dd97e6745164acb3d0733253d730e8', (ROOT / 'bio/bande-empreintes-v2.svg').as_uri()).replace('/_blob/41200b4723504e051b5b0bd1b777ba52', (ROOT / 'bio/bande-empreintes-v3.svg').as_uri())
    p = OUT / name.replace('.dc.html', '.html')
    p.write_text(html)
    return p

import os
which = os.environ.get('SHOTS','main').split(',')
ALL = {
  'main': ('Main.dc.html', 1440, 'main', None),
  'main-mobile': ('Main.dc.html', 390, 'main-mobile', None),
  'v2': ('MainV2.dc.html', 1440, 'v2', None),
  'v2-mobile': ('MainV2.dc.html', 390, 'v2-mobile', None),
  'v2-1000': ('Main.dc.html', 1000, 'v2-1000', None),
  'terr': ('Territoire.dc.html', 1440, 'terr', None),
  'terr-sav': ('Territoire.dc.html', 1440, 'terr-sav', 'button[aria-label^="Savanes"]'),
  'terr-mobile': ('Territoire.dc.html', 390, 'terr-mobile', None),
  'tech': ('Technique.dc.html', 1440, 'tech', None),
  'tech-mobile': ('Technique.dc.html', 390, 'tech-mobile', None),
  'enrol': ('Enrolement.dc.html', 1440, 'enrol', None),
  'enrol-sav': ('Enrolement.dc.html', 1440, 'enrol-sav', '.carte-liste button:has(span:text-is("Kara"))'),
  'main-plat': ('Main.dc.html', 1440, 'main-plat', '.carte-liste button:has(span:text-is("Plateaux"))'),
  'cartes-dagl': ('Cartes.dc.html', 1440, 'cartes-dagl', '.carte-liste button:has(span:text-is("Grand Lomé"))'),
  'cartes': ('Cartes.dc.html', 1440, 'cartes', None),
  'usage': ('Usage.dc.html', 1440, 'usage', None),
  'bio': ('Biometrie.dc.html', 1440, 'bio', None),
  'idps': ('Idps.dc.html', 1440, 'idps', None),
  'idps-mobile': ('Idps.dc.html', 390, 'idps-mobile', None),
  'bio-mobile': ('Biometrie.dc.html', 390, 'bio-mobile', None),
  'bio-1100': ('Biometrie.dc.html', 1100, 'bio-1100', None),
  'bio-1240': ('Biometrie.dc.html', 1240, 'bio-1240', None),
  'bio-iris': ('Biometrie.dc.html', 1440, 'bio-iris', 'button[aria-pressed]:text-is("Iris")'),
  'enrol-mobile': ('Enrolement.dc.html', 390, 'enrol-mobile', None),
  'cartes-mobile': ('Cartes.dc.html', 390, 'cartes-mobile', None),
  'usage-mobile': ('Usage.dc.html', 390, 'usage-mobile', None),
}
shots = [ALL[k] for k in which]
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for name, w, tag, click in shots:
        p = prep(name)
        pg = b.new_page(viewport={'width': w, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(p.as_uri(), wait_until='load', timeout=20000)
        pg.wait_for_timeout(800)
        if click:
            pg.hover(click)
            pg.wait_for_timeout(200)
            pg.click(click)
            pg.wait_for_timeout(300)
        pg.screenshot(path=str(OUT / f'{tag}.png'), full_page=True)
        print(tag, 'errors:', errs, 'height:', pg.evaluate('document.body.scrollHeight'), 'width:', pg.evaluate('document.documentElement.scrollWidth'))
    b.close()
