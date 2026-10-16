import re, pathlib
from common import *

SRC = pathlib.Path(__file__).resolve().parent / 'src_v21'
_terr = (SRC / 'Territoire.dc.html').read_text().split('\n')
_main = (SRC / 'Main.dc.html').read_text()

# Fragments repris de la v2.1
BREADCRUMB = '\n'.join(_terr[101:111])            # <nav aria-label="Fil d'Ariane"> ... </nav>
TERRITORY = '\n'.join(_terr[117:277])             # carte + tableau, puis pyramide + centres
HEBDO = re.search(r'<section aria-labelledby="hebdo".*?</section>', _main, re.S).group(0)
DEVENIR = re.search(r'(<div style="flex: 3 1 560px;.*?)\n\n<div style="flex: 2 1 380px;', _main, re.S).group(1)
assert BREADCRUMB.startswith('<nav') and BREADCRUMB.rstrip().endswith('</nav>'), BREADCRUMB[-40:]
assert TERRITORY.startswith('<div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: stretch">')

FILTERS = PERIODE + select('Région', ['Toutes les régions', 'Grand Lomé', 'Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'],
                           extra_attrs='value="{{regionValue}}" onChange="{{onRegion}}"', values=['', 'DAGL', 'MAR', 'PLA', 'CEN', 'KAR', 'SAV']) \
    + DIVIDER + select('Type de demande', ['Toutes les demandes', 'Nouvelle inscription', 'Mise à jour', 'Récupération de NIU'], min_w=190) \
    + select('Genre', ['Tous', 'Femmes', 'Hommes'], min_w=110) \
    + select('Âge', ['Tous les âges', '0 à 5 ans', '6 à 14 ans', '15 à 18 ans', '19 à 25 ans', '26 à 35 ans', '36 à 45 ans', '46 à 60 ans', 'Plus de 60 ans'], min_w=140)

PREREG = '''<section aria-labelledby="prereg" style="''' + CARD + '''; display: flex; flex-wrap: wrap; gap: 24px 40px">
<div style="flex: 1 1 320px; min-width: 0; display: flex; flex-direction: column; gap: 12px">
<div>
<h2 id="prereg" style="''' + H2 + '''">Pré-inscription</h2>
<p style="''' + SUB + '''">Étape facultative : le citoyen remplit son dossier en ligne et réserve un rendez-vous.</p>
</div>
<div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 12px">
<span style="font-size: 40px; font-weight: 600; letter-spacing: -0.02em; line-height: 1.1; white-space: nowrap">606 850</span>
<span style="font-size: 14px; color: #4B5A6E">demandes de pré-enrôlement</span>
</div>
<div role="img" aria-label="Réservées environ 90 %, en attente de rendez-vous 9,9 %" style="display: flex; gap: 2px; height: 14px; border-radius: 4px; overflow: hidden">
<div style="width: 90.13%; background: #2A78D6"></div>
<div style="width: 9.87%; background: #1BAF7A"></div>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 8px 20px; font-size: 13px; color: #4B5A6E">
<span style="display: inline-flex; align-items: center; gap: 8px"><span aria-hidden="true" style="width: 12px; height: 12px; border-radius: 3px; background: #2A78D6"></span>Rendez-vous réservé</span>
<span style="display: inline-flex; align-items: center; gap: 8px"><span aria-hidden="true" style="width: 12px; height: 12px; border-radius: 3px; background: #1BAF7A"></span>En attente de rendez-vous</span>
</div>
</div>
<div style="flex: 2 1 560px; min-width: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1px; background: #E6EBEF; border: 1px solid #E6EBEF; border-radius: 6px; overflow: hidden">
<sc-for list="{{prereg}}" as="p" hint-placeholder-count="6">
<div style="background: #FFFFFF; padding: 16px 18px; display: flex; flex-direction: column; gap: 2px">
<span style="font-size: 13px; color: #4B5A6E">{{p.label}}</span>
<span style="font-size: 22px; font-weight: 600; color: {{p.valueColor}}">{{p.value}}</span>
<span style="display: flex; gap: 6px; align-items: flex-start; font-size: 12px; color: #4B5A6E">
<sc-if value="{{p.warn}}" hint-placeholder-val="{{false}}"><svg width="12" height="12" viewBox="0 0 24 24" aria-label="À vérifier" style="flex-shrink: 0; margin-top: 3px; fill: #FAB219; stroke: none"><path d="M12 2 1 21h22L12 2z"></path></svg></sc-if>
<span>{{p.detail}}</span>
</span>
</div>
</sc-for>
</div>
</section>
'''

ROW_INSCRIPTION = '''<div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: stretch">
<section aria-label="Devenir des inscriptions" style="flex: 1 1 520px; min-width: 0; background: #FFFFFF; border-radius: 8px; display: flex">
''' + DEVENIR.replace('repeat(auto-fit, minmax(150px, 1fr))', 'repeat(auto-fit, minmax(190px, 1fr))') + '''
</section>
''' + HEBDO.replace('style="flex: 2 1 620px;', 'style="flex: 1 1 620px;') + '''
</div>
'''

TERRITORY_HEAD = '''<div style="display: flex; flex-direction: column; gap: 4px; margin-top: 8px">
''' + BREADCRUMB + '''
<h2 style="margin: 0; font-size: 22px; font-weight: 600; letter-spacing: -0.01em">{{zoneTitle}}</h2>
</div>
'''

BODY = title('Enrôlement : pré-inscription et inscription') + PREREG + ROW_INSCRIPTION + TERRITORY_HEAD + TERRITORY

SCRIPT = r'''class Component extends DCLogic {
  renderVals() {
    const st = this.state || {};
    const sel = st.region || null;
    const tab = st.cscTab || 'top';
    const nf = (n) => Math.round(n).toLocaleString('fr-FR').replace(/[  ]/g, ' ');
    const pct = (x) => x.toFixed(1).replace('.', ',') + ' %';
    const NAT = 3278239;

    // Pré-inscription
    const prereg = [
      { label: 'Rendez-vous réservé', value: '≈ ' + nf(546964), detail: 'Lu sur le graphique : le compteur actuel affiche 0', warn: true, valueColor: '#071B35' },
      { label: 'En attente de rendez-vous', value: nf(59886), detail: '9,9 % des demandes', warn: false, valueColor: '#071B35' },
      { label: 'Expirées', value: '0', detail: 'Aucune expiration enregistrée', warn: false, valueColor: '#071B35' },
      { label: 'Honorées à l’inscription', value: 'À créer', detail: 'Statut « consommée » à exposer pour mesurer la conversion', warn: false, valueColor: '#4B5A6E' },
      { label: 'Pré-inscrits par sexe', value: '53 % / 47 %', detail: 'Hommes / femmes, l’inverse des NIU générés', warn: false, valueColor: '#071B35' },
      { label: 'Dernière demande', value: '14/01/2026', detail: 'à 11h28', warn: false, valueColor: '#071B35' }
    ];

    // Devenir des inscriptions
    const TOTAL = NAT;
    const parts = [
      { label: 'NIU générés', n: 3058886, color: '#B4BFCB', note: '' },
      { label: 'En cours', n: 14455, color: '#2A78D6', note: ', depuis 30 jours ou moins' },
      { label: 'Bloqués', n: 118402, color: '#FAB219', note: ', depuis plus de 30 jours' },
      { label: 'Rejetés', n: 86496, color: '#D03B3B', note: '' }
    ].map((p) => ({
      label: p.label, color: p.color, value: nf(p.n), pct: pct(p.n / TOTAL * 100) + p.note,
      w: (p.n / TOTAL * 100).toFixed(2), tip: p.label + ' : ' + nf(p.n)
    }));

    // Inscriptions et NIU par semaine
    const weeks = [
      ['20/10', 30480, 28610, '20 octobre'], ['27/10', 31250, 29140, '27 octobre'], ['03/11', 33480, 31020, '3 novembre'],
      ['10/11', 35920, 33650, '10 novembre'], ['17/11', 34110, 32480, '17 novembre'], ['24/11', 36870, 34300, '24 novembre'],
      ['01/12', 38240, 35910, '1er décembre'], ['08/12', 37560, 35120, '8 décembre'], ['15/12', 35010, 33060, '15 décembre'],
      ['22/12', 22940, 22410, '22 décembre'], ['29/12', 18620, 17380, '29 décembre'], ['05/01', 21480, 19950, '5 janvier']
    ];
    const hov = typeof st.hover === 'number' ? st.hover : weeks.length - 1;
    const H = 220, MAX = 40000;
    const trend = weeks.map((w, i) => ({
      label: w[0], h: (w[1] / MAX * H).toFixed(1),
      bg: i === hov ? '#1C5CAB' : '#2A78D6',
      band: i === hov ? 'rgba(42,120,214,0.07)' : 'transparent',
      aria: 'Semaine du ' + w[3] + ' : ' + nf(w[1]) + ' inscriptions, ' + nf(w[2]) + ' NIU générés',
      enter: () => this.setState({ hover: i })
    }));
    const hw = weeks[hov];
    const readout = 'Semaine du ' + hw[3] + ' : ' + nf(hw[1]) + ' inscriptions, ' + nf(hw[2]) + ' NIU générés (' + pct(hw[2] / hw[1] * 100) + ').';
    const linePoints = weeks.map((w, i) => ((i + 0.5) * 100).toFixed(1) + ',' + (H - w[2] / MAX * H).toFixed(1)).join(' ');
    const lw = weeks[weeks.length - 1];
    const endDot = { left: ((weeks.length - 0.5) / weeks.length * 100).toFixed(2), bottom: (lw[2] / MAX * H).toFixed(1) };

    // Territoire : région -> préfectures [nom, inscriptions, % rejet, % en cours, délai médian]
    const R = [
      { id: 'SAV', name: 'Savanes', h: 64, prefs: [['Tône', 186239, 3.4, 4.4, 8.0], ['Cinkassé', 74000, 3.8, 4.9, 9.0], ['Oti', 72000, 3.7, 4.8, 9.0], ['Kpendjal', 62000, 4.1, 5.2, 9.5], ['Tandjouaré', 56000, 3.6, 4.7, 8.5]] },
      { id: 'KAR', name: 'Kara', h: 72, prefs: [['Kozah', 142000, 2.6, 4.0, 6.5], ['Bassar', 78000, 3.0, 4.4, 8.0], ['Binah', 52000, 2.9, 4.3, 7.5], ['Doufelgou', 48000, 3.1, 4.5, 8.0], ['Dankpen', 38000, 3.4, 4.9, 9.0], ['Kéran', 28000, 3.2, 4.7, 8.5]] },
      { id: 'CEN', name: 'Centrale', h: 72, prefs: [['Tchaoudjo', 128000, 2.9, 4.2, 7.0], ['Sotouboua', 72000, 3.2, 4.6, 8.0], ['Tchamba', 58000, 3.3, 4.7, 8.5], ['Blitta', 54000, 3.1, 4.5, 8.0]] },
      { id: 'PLA', name: 'Plateaux', h: 100, prefs: [['Ogou', 142000, 2.6, 4.0, 6.5], ['Kloto', 128000, 2.7, 4.1, 7.0], ['Haho', 96000, 2.9, 4.3, 7.5], ['Amou', 62000, 2.8, 4.2, 7.5], ['Est-Mono', 58000, 3.1, 4.6, 8.0], ['Wawa', 56000, 3.0, 4.5, 8.0], ['Agou', 56000, 2.7, 4.1, 7.0]] },
      { id: 'MAR', name: 'Maritime', h: 56, prefs: [['Zio', 168000, 2.3, 3.8, 6.0], ['Lacs', 118000, 2.4, 3.9, 6.5], ['Vo', 82000, 2.5, 4.0, 6.5], ['Avé', 74000, 2.6, 4.1, 7.0], ['Yoto', 46000, 2.7, 4.4, 7.5], ['Bas-Mono', 24000, 2.9, 4.6, 8.0]] },
      { id: 'DAGL', name: 'Grand Lomé', h: 48, prefs: [['Golfe', 612000, 2.0, 3.6, 5.5], ['Agoè-Nyivé', 408000, 2.3, 3.9, 6.0]] }
    ];
    const agg = (prefs) => {
      let n = 0, rj = 0, ec = 0, dl = 0;
      prefs.forEach((p) => { n += p[1]; rj += p[1] * p[2] / 100; ec += p[1] * p[3] / 100; dl += p[1] * p[4]; });
      return { n: n, rejN: rj, coursN: ec, rej: rj / n * 100, cours: ec / n * 100, delai: dl / n };
    };
    const round1 = (x) => Math.round(x * 10) / 10;
    const seq = (r) => r < 2.5 ? '#B7D3F6' : r < 3.0 ? '#6DA7EC' : r < 3.5 ? '#2A78D6' : '#184F95';
    const regions = R.map((r) => Object.assign({ id: r.id, name: r.name, h: r.h, prefs: r.prefs }, agg(r.prefs)));
    const cur = sel ? regions.find((r) => r.id === sel) : null;
    const bands = regions.map((r) => {
      const on = sel === r.id;
      return {
        name: r.name, rej: pct(r.rej), value: nf(r.n), h: r.h, on: on,
        fill: seq(round1(r.rej)), rowBg: on ? '#F1F4F6' : 'transparent', pressed: on ? 'true' : 'false',
        aria: r.name + ' : taux de rejet ' + pct(r.rej) + ', ' + nf(r.n) + ' inscriptions',
        pick: () => this.setState({ region: on ? null : r.id })
      };
    });
    const figures = cur ? [
      { label: 'Inscriptions', value: nf(cur.n), detail: pct(cur.n / NAT * 100) + ' du total national' },
      { label: 'NIU générés', value: pct(100 - cur.rej - cur.cours), detail: nf(cur.n - cur.rejN - cur.coursN) + ' NIU' },
      { label: 'Taux de rejet', value: pct(cur.rej), detail: nf(cur.rejN) + ' demandes' },
      { label: 'En cours', value: nf(cur.coursN), detail: pct(cur.cours) + ' des inscriptions' },
      { label: 'Délai médian', value: cur.delai.toFixed(1).replace('.', ',') + ' jours', detail: 'jusqu’au NIU' }
    ] : [
      { label: 'Inscriptions', value: nf(NAT), detail: 'dans 6 régions' },
      { label: 'NIU générés', value: '93,3 %', detail: nf(3058886) + ' NIU' },
      { label: 'Taux de rejet', value: '2,6 %', detail: nf(86496) + ' demandes' },
      { label: 'En cours', value: nf(132857), detail: '4,1 % des inscriptions' },
      { label: 'Délai médian', value: '6,5 jours', detail: 'jusqu’au NIU' }
    ];
    const src = cur
      ? cur.prefs.map((p) => ({ name: p[0], n: p[1], rej: p[2], cours: p[3], delai: p[4], coursN: p[1] * p[3] / 100, id: null }))
      : regions.map((r) => ({ name: r.name, n: r.n, rej: r.rej, cours: r.cours, delai: r.delai, coursN: r.coursN, id: r.id }));
    src.sort((a, b) => b.n - a.n);
    const maxN = Math.max.apply(null, src.map((s) => s.n));
    const rows = src.map((s) => ({
      name: s.name, canDrill: !cur, cannotDrill: !!cur,
      drill: () => this.setState({ region: s.id }),
      value: nf(s.n), w: (s.n / maxN * 70).toFixed(1),
      tip: s.name + ' : ' + nf(s.n) + ' inscriptions',
      niu: pct(100 - s.rej - s.cours), rej: pct(s.rej),
      high: round1(s.rej) >= 3.5, rejWeight: round1(s.rej) >= 3.5 ? '600' : '400',
      cours: nf(s.coursN), delai: s.delai.toFixed(1).replace('.', ',') + ' j'
    }));
    const bins = [['60 ans et +', 4.1, 2.7], ['46 à 60', 8.4, 7.2], ['36 à 45', 9.3, 8.1], ['26 à 35', 12.6, 11.1], ['19 à 25', 9.4, 8.4], ['15 à 18', 3.8, 3.7], ['6 à 14', 4.3, 4.6], ['0 à 5', 1.1, 1.2]];
    const pyramid = bins.map((b) => ({ label: b[0], f: pct(b[1]), m: pct(b[2]), wf: (b[1] / 12.6 * 78).toFixed(1), wm: (b[2] / 12.6 * 78).toFixed(1) }));
    const top = [
      ['EPP Doumassesse I G/B', 'Golfe, Grand Lomé', 'DAGL', 43534],
      ['CEG Baguida Centre, Port de pêche', 'Golfe, Grand Lomé', 'DAGL', 15971],
      ['EPP Worgou G/A', 'Tône, Savanes', 'SAV', 12404],
      ['EPP Gbetsogbe, Port autonome', 'Golfe, Grand Lomé', 'DAGL', 11919],
      ['Lycée Nassable', 'Tône, Savanes', 'SAV', 10109]
    ];
    const watch = [
      ['Centre n° 60412', 'Kpendjal, Savanes', 'SAV', 9.6, 8230],
      ['Centre n° 60227', 'Oti, Savanes', 'SAV', 8.7, 8520],
      ['Centre n° 50318', 'Dankpen, Kara', 'KAR', 8.1, 7980],
      ['Centre n° 40105', 'Tchamba, Centrale', 'CEN', 7.7, 7800],
      ['Centre n° 20533', 'Bas-Mono, Maritime', 'MAR', 7.2, 7430]
    ];
    const inZone = (c) => !sel || c[2] === sel;
    const topList = top.filter(inZone).map((c, i) => ({ rank: String(i + 1), name: c[0], place: c[1], metric: nf(c[3]), sub: 'inscriptions' }));
    const watchList = watch.filter(inZone).map((c, i) => ({ rank: String(i + 1), name: c[0], place: c[1], metric: pct(c[3]), sub: 'de rejets sur ' + nf(c[4]) }));
    const cscRows = tab === 'top' ? topList : watchList;
    const tabBtn = (key) => ({
      pressed: tab === key ? 'true' : 'false',
      bg: tab === key ? '#FFFFFF' : 'transparent',
      fg: tab === key ? '#071B35' : '#4B5A6E',
      shadow: tab === key ? '0 0 0 1px #DCE3E9' : 'none',
      pick: () => this.setState({ cscTab: key })
    });

    return {
      prereg: prereg, parts: parts, trend: trend, readout: readout, linePoints: linePoints, endDot: endDot,
      isRegion: !!cur, isNational: !cur,
      regionName: cur ? cur.name : '',
      regionValue: sel || '',
      onRegion: (e) => this.setState({ region: e && e.target && e.target.value ? e.target.value : null }),
      goNational: () => this.setState({ region: null }),
      zoneTitle: cur ? 'Territoire : région ' + cur.name : 'Territoire : vue nationale',
      zoneLabel: cur ? 'Région ' + cur.name : 'Ensemble du Togo',
      bands: bands, figures: figures, rows: rows,
      tableTitle: cur ? 'Préfectures de la région ' + cur.name : 'Régions',
      tableHint: cur ? 'Niveaux suivants : commune, canton, localité, centre' : 'Choisissez une région pour voir ses préfectures',
      pyramid: pyramid,
      tabTop: tabBtn('top'), tabWatch: tabBtn('watch'),
      cscRows: cscRows, hasCsc: cscRows.length > 0, noCsc: cscRows.length === 0,
      emptyText: tab === 'top' ? 'Aucun des centres les plus actifs du pays ne se trouve dans cette région.' : 'Aucun centre de cette région ne dépasse le seuil de rejet à surveiller.',
      metricLabel: tab === 'top' ? 'Inscriptions' : 'Taux de rejet'
    };
  }
}'''

FOOTER = 'Maquette v3. Les totaux nationaux, les chiffres de pré-inscription et les cinq centres les plus actifs viennent du BI actuel. Tendances, régions, préfectures, démographie et centres à surveiller sont fictifs.'


def build():
    return page('Enrôlement', 'Enrolement.dc.html', FILTERS, BODY, SCRIPT, 2490, FOOTER)

# ---------- v3.1 : carte interactive du Togo ----------
import common_map as CM

MAP_SECTION = '''<section aria-labelledby="carte" style="flex: 0 1 560px; max-width: 100%; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 12px">
<div>
<h2 id="carte" style="''' + H2 + '''">Carte du Togo</h2>
<p style="''' + SUB + '''">Couleur selon le taux de rejet. Cliquez sur une région pour afficher ses préfectures.</p>
</div>
''' + CM.block('map', 470, CM.legend('Taux de rejet', ['&lt; 2,5 %', '2,5 à 3 %', '3 à 3,5 %', '3,5 % et +']), brackets=True) + '''</section>'''

_new_terr, _n = re.subn(r'<section aria-labelledby="carte".*?</section>', lambda m: MAP_SECTION, TERRITORY, count=1, flags=re.S)
assert _n == 1
BODY = BODY.replace(TERRITORY, _new_terr)

_script, _n = re.subn(r'const R = \[.*?\n    \];', lambda m: 'const R = ' + CM.PREFS_JS + ';', SCRIPT, count=1, flags=re.S)
assert _n == 1
MAP_JS = r'''
    const hoverName = st.mapHover || null;
    const prefIndex = {};
    R.forEach((r) => r.prefs.forEach((p) => { prefIndex[p[0]] = p; }));
    const regByName = {};
    regions.forEach((r) => { regByName[r.name] = r; });
    const map = this.buildMap({
      sel: sel, hover: hoverName,
      classes: [[2.5, '#B7D3F6'], [3.0, '#6DA7EC'], [3.5, '#2A78D6'], [99, '#184F95']],
      regionValue: (n) => round1(regByName[n].rej),
      prefValue: (n) => prefIndex[n][2],
      onPick: (id) => this.setState({ region: id, mapHover: null }),
      onHover: (n) => this.setState({ mapHover: n }),
      describe: (n, isPref) => isPref
        ? n + ' : ' + pct(prefIndex[n][2]) + ' de rejets, ' + nf(prefIndex[n][1]) + ' inscriptions, délai médian ' + String(prefIndex[n][4]).replace('.', ',') + ' j'
        : n + ' : ' + pct(regByName[n].rej) + ' de rejets, ' + nf(regByName[n].n) + ' inscriptions',
      national: 'Togo : ' + pct(86496 / 3278239 * 100) + ' de rejets, ' + nf(3278239) + ' inscriptions',
      px: 470, ar: 0.62, fmt: (v) => pct(v), nationalValue: pct(86496 / 3278239 * 100)
    });
'''
_anchor = '    return {\n      prereg: prereg,'
assert _anchor in _script
_script = _script.replace(_anchor, MAP_JS + _anchor).replace('      prereg: prereg,', '      map: map,\n      prereg: prereg,', 1)
SCRIPT = CM.inject(_script)
BODY = BODY.replace('<section aria-label="Chiffres de la zone" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));',
                    '<section aria-label="Chiffres de la zone" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));')
assert 'minmax(140px, 1fr))' in BODY
assert BODY.count('padding: 18px 20px; display: flex; flex-direction: column; gap: 2px') == 1
BODY = BODY.replace('padding: 18px 20px; display: flex; flex-direction: column; gap: 2px', 'padding: 18px 16px; display: flex; flex-direction: column; gap: 2px')
FOOTER = FOOTER + ' Contours des régions et préfectures : geoBoundaries, d’après OpenStreetMap.'
