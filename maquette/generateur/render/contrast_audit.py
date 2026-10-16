exec(open('shoot.py').read().split('import os')[0])
from playwright.sync_api import sync_playwright
JS = r"""() => {
  const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const blend = (top, bot) => ({ r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1 });
  const bgOf = (el) => { let stack = []; for (let e = el; e; e = e.parentElement) { const cs = getComputedStyle(e); const c = parse(cs.backgroundColor); if (cs.backgroundImage && cs.backgroundImage !== 'none' && !(c && c.a > 0)) return null; if (c && c.a > 0) { stack.push(c); if (c.a >= 1) break; } } let res = { r: 255, g: 255, b: 255, a: 1 }; for (let i = stack.length - 1; i >= 0; i--) res = blend(stack[i], res); return res; };
  const out = [];
  document.querySelectorAll('body *').forEach((el) => {
    if (!el.offsetParent && getComputedStyle(el).position !== 'fixed') return;
    const txt = Array.from(el.childNodes).filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join(' ').trim();
    if (!txt) return;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || +cs.opacity === 0) return;
    if (el.closest('[aria-disabled=true]')) return;
    let fg = parse(cs.color); const bg = bgOf(el); if (!fg || !bg) return;
    if (fg.a < 1) fg = blend(fg, bg);
    const L1 = lum(fg), L2 = lum(bg); const cr = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const size = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 700; const large = size >= 24 || (bold && size >= 18.66);
    if (cr < (large ? 3 : 4.5)) out.push({ t: txt.slice(0, 40), cr: Math.round(cr * 100) / 100, fs: size, col: cs.color });
  });
  return out;
}"""
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for name in ['Main', 'Enrolement', 'Cartes', 'Biometrie', 'Idps', 'Usage', 'Technique']:
        pg = b.new_page(viewport={'width': 1440, 'height': 900})
        pg.goto(prep(name + '.dc.html').as_uri(), wait_until='load'); pg.wait_for_timeout(500)
        r = pg.evaluate(JS)
        print(name, len(r))
        seen = set()
        for x in r:
            k = (x['col'], x['cr'])
            if k in seen: continue
            seen.add(k); print('   ', x)
        pg.close()
    b.close()
