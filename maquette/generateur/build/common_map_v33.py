"""Carte interactive du Togo (régions -> préfectures), partagée par plusieurs pages."""
import json, pathlib
from common import BRACKETS

_G = json.load(open(pathlib.Path(__file__).resolve().parent / 'togo_svg.json'))
GEO_LITERAL = json.dumps({'W': _G['W'], 'H': _G['H'],
                          'regions': [{k: r[k] for k in ('name', 'd', 'lx', 'ly', 'bb')} for r in _G['regions']],
                          'prefs': [{k: p[k] for k in ('name', 'region', 'd', 'lx', 'ly', 'bb')} for p in _G['prefs']]},
                         ensure_ascii=False, separators=(',', ':'))

# Préfectures (découpage geoBoundaries / OSM 2017) : [nom, inscriptions, % rejet, % en cours, délai médian en jours]
PREFS_JS = r'''[
      { id: 'SAV', name: 'Savanes', prefs: [['Tône', 186239, 3.4, 4.4, 8.0], ['Cinkassé', 74000, 3.8, 4.9, 9.0], ['Oti', 72000, 3.7, 4.8, 9.0], ['Kpendjal', 62000, 4.1, 5.2, 9.5], ['Tandjouaré', 56000, 3.6, 4.7, 8.5]] },
      { id: 'KAR', name: 'Kara', prefs: [['Kozah', 132000, 2.6, 4.0, 6.5], ['Bassar', 70000, 3.0, 4.4, 8.0], ['Binah', 50000, 2.9, 4.3, 7.5], ['Doufelgou', 46000, 3.1, 4.5, 8.0], ['Dankpen', 36000, 3.4, 4.9, 9.0], ['Kéran', 28000, 3.2, 4.7, 8.5], ['Assoli', 24000, 3.1, 4.6, 8.0]] },
      { id: 'CEN', name: 'Centrale', prefs: [['Tchaoudjo', 118000, 2.9, 4.2, 7.0], ['Sotouboua', 68000, 3.2, 4.6, 8.0], ['Tchamba', 54000, 3.3, 4.7, 8.5], ['Blitta', 46000, 3.1, 4.5, 8.0], ['Mô', 26000, 3.4, 4.8, 8.5]] },
      { id: 'PLA', name: 'Plateaux', prefs: [['Ogou', 104000, 2.6, 4.0, 6.5], ['Kloto', 88000, 2.7, 4.1, 7.0], ['Haho', 72000, 2.9, 4.3, 7.5], ['Amou', 46000, 2.8, 4.2, 7.5], ['Anié', 44000, 2.9, 4.3, 7.5], ['Est-Mono', 42000, 3.1, 4.6, 8.0], ['Wawa', 40000, 3.0, 4.5, 8.0], ['Agou', 40000, 2.7, 4.1, 7.0], ['Moyen-Mono', 34000, 3.0, 4.4, 8.0], ['Kpélé', 32000, 2.7, 4.1, 7.0], ['Danyi', 30000, 2.8, 4.2, 7.5], ['Akébou', 26000, 3.1, 4.5, 8.0]] },
      { id: 'MAR', name: 'Maritime', prefs: [['Zio', 168000, 2.3, 3.8, 6.0], ['Lacs', 118000, 2.4, 3.9, 6.5], ['Vo', 82000, 2.5, 4.0, 6.5], ['Avé', 74000, 2.6, 4.1, 7.0], ['Yoto', 46000, 2.7, 4.4, 7.5], ['Bas-Mono', 24000, 2.9, 4.6, 8.0]] },
      { id: 'DAGL', name: 'Grand Lomé', prefs: [['Golfe', 640000, 2.2, 3.8, 6.0], ['Lomé', 380000, 1.9, 3.5, 5.0]] }
    ]'''

METHODS = r'''
  geo() {
    if (!this._geo) this._geo = %s;
    return this._geo;
  }

  buildMap(c) {
    const G = this.geo();
    const ids = { 'Savanes': 'SAV', 'Kara': 'KAR', 'Centrale': 'CEN', 'Plateaux': 'PLA', 'Maritime': 'MAR', 'Grand Lomé': 'DAGL' };
    const names = {};
    Object.keys(ids).forEach((n) => { names[ids[n]] = n; });
    const color = (v) => {
      for (let i = 0; i < c.classes.length; i++) { if (v < c.classes[i][0]) return c.classes[i][1]; }
      return c.classes[c.classes.length - 1][1];
    };
    const selName = c.sel ? names[c.sel] : null;
    // ne relance un rendu que si la zone survolée change (évite les boucles de survol)
    const hoverTo = (n) => { if ((c.hover || null) !== (n || null)) c.onHover(n || null); };
    const px = c.px || 440;
    const AR = c.ar || 0.72;
    let shapes, labels, viewBox, outlines = [];
    if (!selName) {
      shapes = G.regions.map((r) => {
        const hov = c.hover === r.name;
        return { d: r.d, fill: color(c.regionValue(r.name)), stroke: hov ? '#071B35' : '#FFFFFF', sw: hov ? '2.5' : '1.2', cursor: 'pointer',
          pick: () => c.onPick(ids[r.name]), enter: () => hoverTo(r.name) };
      });
      const vh = G.H + 40;
      viewBox = (-14) + ' ' + (-8) + ' ' + (G.W + 28) + ' ' + vh;
      const fs = (11.5 * vh / px).toFixed(1);
      labels = G.regions.map((r) => {
        const dl = r.name === 'Grand Lomé';
        return { t: r.name, x: dl ? (r.bb[0] + r.bb[2] / 2).toFixed(1) : r.lx, y: dl ? (r.bb[1] + r.bb[3] + 16).toFixed(1) : (r.ly + 3).toFixed(1), fs: fs, halo: (fs * 0.35).toFixed(1) };
      });
    } else {
      const reg = G.regions.find((r) => r.name === selName);
      const others = G.regions.filter((r) => r.name !== selName).map((r) => ({
        d: r.d, fill: '#E6EBEF', stroke: '#FFFFFF', sw: '1.2', cursor: 'pointer',
        pick: () => c.onPick(ids[r.name]), enter: () => hoverTo(null)
      }));
      const prefs = G.prefs.filter((p) => p.region === selName).map((p) => {
        const hov = c.hover === p.name;
        return { d: p.d, fill: color(c.prefValue(p.name, selName)), stroke: hov ? '#071B35' : '#FFFFFF', sw: hov ? '2.5' : '1', cursor: 'default',
          pick: () => hoverTo(p.name), enter: () => hoverTo(p.name) };
      });
      shapes = others.concat(prefs);
      outlines = [{ d: reg.d }];
      const b = reg.bb;
      // cadrage ajusté à la zone de dessin (largeur / hauteur = AR) au lieu d'un carré
      const vw = Math.max(b[2] * 1.25, b[3] * 1.25 * AR), vh = vw / AR;
      const cx = b[0] + b[2] / 2, cy = b[1] + b[3] / 2;
      viewBox = (cx - vw / 2).toFixed(1) + ' ' + (cy - vh / 2).toFixed(1) + ' ' + vw.toFixed(1) + ' ' + vh.toFixed(1);
      const fs = (10.5 * vh / px).toFixed(2);
      labels = G.prefs.filter((p) => p.region === selName).map((p) => ({ t: p.name, x: p.lx, y: (p.ly + Number(fs) / 3).toFixed(2), fs: fs, halo: (fs * 0.35).toFixed(2) }));
    }
    const target = c.hover || selName;
    const readout = target ? c.describe(target, !!selName && target !== selName) : c.national;

    // Aside : Togo, puis les régions du nord au sud ; région ouverte = ses préfectures du nord au sud
    const ORDER = ['Savanes', 'Kara', 'Centrale', 'Plateaux', 'Maritime', 'Grand Lomé'];
    const item = (o, on, hv) => {
      const it = Object.assign({ swatch: 'transparent', ring: 'transparent', hasBar: false, w: '0', sub: '', pad: '10px', minH: '40px', fs: '13px', weight: '600' }, o);
      it.bg = on ? '#013781' : (hv ? '#E3EAF3' : 'transparent');
      it.fg = on ? '#FFFFFF' : '#071B35';
      it.mark = on ? '#FCBA21' : 'transparent';
      it.ring = on ? '#FFFFFF' : 'rgba(7, 27, 53, 0.15)';
      if (it.swatch === 'transparent') it.ring = 'transparent';
      it.barColor = on ? '#B7D3F6' : '#2A78D6';
      it.subFg = on ? '#D6E0F2' : '#4B5A6E';
      it.pressed = on ? 'true' : 'false';
      return it;
    };
    const withBar = (it, n) => {
      if (!c.bar) return it;
      const b = c.bar(n);
      return Object.assign(it, { hasBar: true, w: b.w, sub: b.sub });
    };
    const items = [withBar(item({ name: 'Togo', value: c.nationalValue || '', pick: () => c.onPick(null), enter: () => hoverTo(null) }, !selName, false), null)];
    if (!selName) {
      ORDER.forEach((n) => {
        const v = c.regionValue(n);
        items.push(withBar(item({ name: n, value: c.fmt(v), swatch: color(v), pick: () => c.onPick(ids[n]), enter: () => hoverTo(n) }, false, c.hover === n), n));
      });
    } else {
      const v = c.regionValue(selName);
      items.push(withBar(item({ name: selName, value: c.fmt(v), swatch: color(v), pick: () => hoverTo(null), enter: () => hoverTo(null) }, true, false), selName));
      G.prefs.filter((p) => p.region === selName).slice().sort((a, b) => a.ly - b.ly).forEach((p) => {
        const pv = c.prefValue(p.name, selName);
        const hv = c.hover === p.name;
        const it = item({ name: p.name, value: c.fmt(pv), swatch: color(pv), pad: '26px', minH: '30px', fs: '12.5px', weight: '500',
          pick: () => hoverTo(p.name), enter: () => hoverTo(p.name) }, false, hv);
        it.pressed = hv ? 'true' : 'false';
        items.push(it);
      });
    }
    return {
      viewBox: viewBox, shapes: shapes, outlines: outlines, labels: labels, readout: readout, items: items,
      asideTitle: selName ? 'Préfectures, du nord au sud' : 'Régions, du nord au sud',
      leave: () => hoverTo(null),
      aria: selName ? 'Carte de la région ' + selName + ' et de ses préfectures' : 'Carte des régions du Togo'
    };
  }
''' % GEO_LITERAL


def inject(script):
    head = 'class Component extends DCLogic {'
    assert script.startswith(head)
    return head + METHODS + script[len(head):]


def map_svg(var='map', height=500, brackets=False):
    br = BRACKETS.replace('top: 14px', 'top: 0').replace('bottom: 14px', 'bottom: 0').replace('left: 14px', 'left: 0').replace('right: 14px', 'right: 0') if brackets else ''
    return '''<div style="position: relative; padding: 10px">
''' + br + '''<svg viewBox="{{%(v)s.viewBox}}" role="img" aria-label="{{%(v)s.aria}}" onMouseLeave="{{%(v)s.leave}}" style="display: block; width: 100%%; height: %(h)dpx; overflow: hidden">
<sc-for list="{{%(v)s.shapes}}" as="s" hint-placeholder-count="6">
<path d="{{s.d}}" onClick="{{s.pick}}" onMouseEnter="{{s.enter}}" style="fill: {{s.fill}}; stroke: {{s.stroke}}; stroke-width: {{s.sw}}px; stroke-linejoin: round; vector-effect: non-scaling-stroke; cursor: {{s.cursor}}"></path>
</sc-for>
<sc-for list="{{%(v)s.outlines}}" as="o" hint-placeholder-count="0">
<path d="{{o.d}}" style="fill: none; stroke: #071B35; stroke-width: 1.8px; stroke-linejoin: round; vector-effect: non-scaling-stroke; pointer-events: none"></path>
</sc-for>
<sc-for list="{{%(v)s.labels}}" as="l" hint-placeholder-count="6">
<text x="{{l.x}}" y="{{l.y}}" text-anchor="middle" style="font-family: Poppins, sans-serif; font-size: {{l.fs}}px; font-weight: 600; fill: #071B35; paint-order: stroke; stroke: #FFFFFF; stroke-width: {{l.halo}}px; stroke-linejoin: round; pointer-events: none">{{l.t}}</text>
</sc-for>
</svg>
</div>
''' % {'v': var, 'h': height}


def readout(var='map'):
    return '<p aria-live="polite" style="margin: 0; padding: 8px 12px; border-radius: 6px; background: #F1F4F6; font-size: 13px; min-height: 40px; box-sizing: border-box">{{%s.readout}}</p>\n' % var


def legend(title, labels, colors=('#B7D3F6', '#6DA7EC', '#2A78D6', '#184F95')):
    sw = ''.join('<span style="height: 10px; background: %s"></span>' % c for c in colors)
    lb = ''.join('<span>%s</span>' % l for l in labels)
    return ('<div style="display: flex; flex-direction: column; gap: 6px">\n<span style="font-size: 12px; color: #4B5A6E">%s</span>\n'
            '<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 2px">%s</div>\n'
            '<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 2px; font-size: 12px; color: #4B5A6E; font-variant-numeric: tabular-nums">%s</div>\n</div>\n'
            % (title, sw, lb))


def region_buttons(var='mapButtons'):
    return '''<div role="group" aria-label="Choisir une région" style="display: flex; flex-wrap: wrap; gap: 6px">
<sc-for list="{{%s}}" as="b" hint-placeholder-count="7">
<button type="button" onClick="{{b.pick}}" aria-pressed="{{b.pressed}}" style="min-height: 44px; padding: 0 12px; border: 1px solid {{b.border}}; border-radius: 6px; background: {{b.bg}}; font-family: inherit; font-size: 13px; font-weight: 600; color: {{b.fg}}; cursor: pointer">{{b.name}}</button>
</sc-for>
</div>
''' % var


def aside(var='map', width=200):
    return '''<aside aria-label="Zones de la carte" class="carte-aside" style="flex-basis: %(w)dpx">
<span style="font-size: 12px; font-weight: 500; color: #4B5A6E">{{%(v)s.asideTitle}}</span>
<p aria-live="polite" class="carte-lecture">{{%(v)s.readout}}</p>
<div role="group" aria-label="Choisir une zone" class="carte-liste" onMouseLeave="{{%(v)s.leave}}">
<sc-for list="{{%(v)s.items}}" as="b" hint-placeholder-count="7">
<button type="button" onClick="{{b.pick}}" onMouseEnter="{{b.enter}}" aria-pressed="{{b.pressed}}" style="display: grid; grid-template-columns: 12px minmax(0, 1fr) auto; align-items: center; gap: 2px 10px; min-height: {{b.minH}}; padding: 5px 10px 5px {{b.pad}}; border: 0; border-left: 3px solid {{b.mark}}; border-radius: 4px; background: {{b.bg}}; text-align: left; font-family: inherit; font-size: {{b.fs}}; color: {{b.fg}}; cursor: pointer">
<span aria-hidden="true" style="width: 12px; height: 12px; border-radius: 3px; background: {{b.swatch}}; box-shadow: inset 0 0 0 1px {{b.ring}}"></span>
<span style="font-weight: {{b.weight}}; line-height: 1.25">{{b.name}}</span>
<span style="font-weight: 600; font-variant-numeric: tabular-nums; white-space: nowrap">{{b.value}}</span>
<sc-if value="{{b.hasBar}}" hint-placeholder-val="{{false}}">
<span style="grid-column: 2 / 4; display: flex; align-items: center; gap: 8px; font-size: 12px; color: {{b.subFg}}; font-variant-numeric: tabular-nums"><span style="height: 6px; width: {{b.w}}%%; background: {{b.barColor}}; border-radius: 0 3px 3px 0"></span><span style="white-space: nowrap">{{b.sub}}</span></span>
</sc-if>
</button>
</sc-for>
</div>
</aside>
''' % {'v': var, 'w': width}


def block(var='map', height=440, legend_html='', brackets=False, aside_w=200):
    """Aside (zones) devant la carte, puis carte + légende + source."""
    return ('<div class="carte-duo">\n' + aside(var, aside_w) + '<div class="carte-zone">\n'
            + map_svg(var, height, brackets) + legend_html + ATTRIBUTION + '</div>\n</div>\n')


ATTRIBUTION = '<p style="margin: 0; font-size: 11px; color: #4B5A6E">Contours : geoBoundaries, d’après © les contributeurs d’OpenStreetMap (découpage 2017, 37 préfectures). À remplacer par le découpage officiel.</p>\n'

# JS : boutons de régions (accès clavier) + Togo
BUTTONS_JS_OLD = r'''
    const mapBtnList = [['', 'Togo'], ['SAV', 'Savanes'], ['KAR', 'Kara'], ['CEN', 'Centrale'], ['PLA', 'Plateaux'], ['MAR', 'Maritime'], ['DAGL', 'Grand Lomé']];
    const mapButtons = mapBtnList.map((b) => {
      const on = (sel || '') === b[0];
      return { name: b[1], pressed: on ? 'true' : 'false', bg: on ? '#013781' : '#FFFFFF', border: on ? '#013781' : '#C5CFDA',
        pick: () => this.setState({ region: b[0] || null, mapHover: null }) };
    }).map((b) => Object.assign(b, { fg: b.pressed === 'true' ? '#FFFFFF' : '#071B35' }));
'''

BUTTONS_JS = ''
NATIONAL_HINT = 'Survolez ou choisissez une zone pour lire ses chiffres.'
