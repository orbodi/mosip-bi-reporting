from common import *

FILTERS = PERIODE + REGION

BODY = title('Cartes e-ID : impression et remise') + '''
<section aria-labelledby="remise" style="position: relative; background: #FFFFFF; border-radius: 8px; padding: 36px 40px; box-sizing: border-box; display: flex; flex-wrap: wrap; gap: 28px 56px; align-items: center">
''' + BRACKETS + '''<div style="flex: 1 1 340px; display: flex; flex-direction: column; gap: 6px">
<h2 id="remise" style="margin: 0; font-size: 15px; font-weight: 500; color: #4B5A6E">Cartes à remettre</h2>
<span style="font-size: clamp(40px, 9vw, 56px); font-weight: 600; letter-spacing: -0.02em; line-height: 1.05; white-space: nowrap">1 330 794</span>
<p style="margin: 4px 0 0; font-size: 15px">42,9 % des cartes expédiées n’ont pas encore été remises à leur titulaire.</p>
<p style="margin: 0; font-size: 13px; color: #4B5A6E">Écart entre les cartes expédiées (3 101 590) et les cartes livrées (1 770 796).</p>
</div>
<div style="flex: 2 1 520px; min-width: 0; display: flex; flex-direction: column; gap: 14px">
<h3 style="margin: 0; font-size: 15px; font-weight: 600">Parcours de la carte</h3>
<sc-for list="{{flow}}" as="f" hint-placeholder-count="3">
<div title="{{f.tip}}" style="display: grid; grid-template-columns: 170px minmax(0, 1fr); gap: 4px 16px; align-items: center">
<span style="font-size: 13px; font-weight: 500">{{f.label}}</span>
<span style="display: flex; align-items: center; gap: 10px">
<span style="height: 18px; width: {{f.w}}%; background: {{f.color}}; border-radius: 0 4px 4px 0"></span>
<span style="font-size: 14px; font-weight: 600; white-space: nowrap; font-variant-numeric: tabular-nums">{{f.value}}</span>
</span>
<span></span>
<span style="font-size: 12px; color: #4B5A6E">{{f.note}}</span>
</div>
</sc-for>
<p style="margin: 4px 0 0; padding-top: 12px; border-top: 1px solid #E6EBEF; font-size: 13px; color: #4B5A6E">11 835 demandes attendent encore l’impression. 6 demandes ont été rejetées, la dernière le 13/03/2026.</p>
</div>
</section>

<div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: stretch">

<section aria-labelledby="parregion" style="flex: 1 1 520px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 10px">
<div>
<h2 id="parregion" style="''' + H2 + '''">Cartes à remettre par région</h2>
<p style="''' + SUB + '''">Nombre de cartes expédiées non livrées, et part des cartes expédiées dans la région.</p>
</div>
<div role="table" aria-label="Cartes à remettre par région" style="font-variant-numeric: tabular-nums">
<div role="row" style="display: grid; grid-template-columns: 110px minmax(0, 1fr) 64px; gap: 12px; padding: 6px 0; font-size: 12px; color: #4B5A6E">
<span role="columnheader">Région</span><span role="columnheader">Cartes à remettre</span><span role="columnheader" style="text-align: right">Part</span>
</div>
<sc-for list="{{byRegion}}" as="r" hint-placeholder-count="6">
<div role="row" title="{{r.tip}}" style="display: grid; grid-template-columns: 110px minmax(0, 1fr) 64px; gap: 12px; align-items: center; padding: 9px 0; border-top: 1px solid #EEF2F5">
<span role="rowheader" style="font-weight: 500">{{r.name}}</span>
<span role="cell" style="display: flex; align-items: center; gap: 10px"><span style="height: 12px; width: {{r.w}}%; background: #2A78D6; border-radius: 0 4px 4px 0"></span><span style="white-space: nowrap">{{r.value}}</span></span>
<span role="cell" style="text-align: right; font-weight: {{r.weight}}">{{r.part}}</span>
</div>
</sc-for>
</div>
</section>

<section aria-labelledby="anciennete" style="flex: 1 1 420px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 12px">
<div>
<h2 id="anciennete" style="''' + H2 + '''">Depuis quand ces cartes attendent</h2>
<p style="''' + SUB + '''">Temps écoulé depuis l’expédition, à la date des dernières données.</p>
</div>
<sc-for list="{{ages}}" as="a" hint-placeholder-count="4">
<div title="{{a.tip}}" style="display: grid; grid-template-columns: 120px minmax(0, 1fr); gap: 12px; align-items: center">
<span style="font-size: 13px">{{a.label}}</span>
<span style="display: flex; align-items: center; gap: 10px"><span style="height: 18px; width: {{a.w}}%; background: {{a.color}}; border-radius: 0 4px 4px 0"></span><span style="font-size: 13px; font-weight: 600; white-space: nowrap; font-variant-numeric: tabular-nums">{{a.value}}</span></span>
</div>
</sc-for>
<p style="margin: auto 0 0; font-size: 13px; color: #4B5A6E">42 % des cartes à remettre attendent depuis plus de six mois.</p>
</section>

</div>

<section aria-labelledby="centres" style="''' + CARD + '''; display: flex; flex-direction: column; gap: 10px">
<div>
<h2 id="centres" style="''' + H2 + '''">Remise des cartes par centre</h2>
<p style="''' + SUB + '''">Croisement des deux classements actuels (cartes expédiées et cartes livrées). Ils ne retiennent pas tout à fait les mêmes centres.</p>
</div>
<div style="overflow-x: auto">
<div role="table" aria-label="Remise des cartes par centre" style="min-width: 720px; font-variant-numeric: tabular-nums">
<div role="row" style="display: grid; grid-template-columns: minmax(220px, 1.4fr) 140px 110px 110px minmax(200px, 1.4fr); gap: 16px; padding: 6px 0; font-size: 12px; color: #4B5A6E">
<span role="columnheader">Centre</span><span role="columnheader">Préfecture, région</span><span role="columnheader" style="text-align: right">Expédiées</span><span role="columnheader" style="text-align: right">Livrées</span><span role="columnheader">Part des cartes remises</span>
</div>
<sc-for list="{{centres}}" as="c" hint-placeholder-count="6">
<div role="row" style="display: grid; grid-template-columns: minmax(220px, 1.4fr) 140px 110px 110px minmax(200px, 1.4fr); gap: 16px; align-items: center; padding: 10px 0; border-top: 1px solid #EEF2F5">
<span role="rowheader" style="font-weight: 500">{{c.name}}</span>
<span role="cell" style="color: #4B5A6E">{{c.place}}</span>
<span role="cell" style="text-align: right; color: {{c.expColor}}">{{c.exp}}</span>
<span role="cell" style="text-align: right; color: {{c.livColor}}">{{c.liv}}</span>
<span role="cell" style="display: flex; align-items: center; gap: 10px">
<sc-if value="{{c.hasPart}}" hint-placeholder-val="{{true}}"><span style="flex-grow: 1; height: 12px; background: #EEF2F5; border-radius: 0 4px 4px 0"><span style="display: block; height: 12px; width: {{c.w}}%; background: #2A78D6; border-radius: 0 4px 4px 0"></span></span><span style="width: 52px; text-align: right; font-weight: 600">{{c.part}}</span></sc-if>
<sc-if value="{{c.noPart}}" hint-placeholder-val="{{false}}"><span style="font-size: 13px; color: #4B5A6E">{{c.missing}}</span></sc-if>
</span>
</div>
</sc-for>
</div>
</div>
</section>

<section aria-labelledby="reconcil" style="''' + CARD + '''; display: flex; flex-wrap: wrap; gap: 20px 48px">
<div style="flex: 1 1 300px; display: flex; flex-direction: column; gap: 8px">
<h2 id="reconcil" style="''' + H2 + '''">Plus de cartes que de NIU</h2>
<p style="margin: 0; font-size: 14px">Le BI compte 42 704 cartes imprimées de plus que de NIU générés, et 54 545 demandes d’impression de plus.</p>
<p style="margin: 0; font-size: 13px; color: #4B5A6E">Pistes à vérifier : réimpressions, nouvelles cartes après une mise à jour, demandes envoyées deux fois au partenaire d’impression.</p>
</div>
<div role="table" aria-label="Réconciliation entre NIU et cartes" style="flex: 2 1 520px; min-width: 0; display: flex; flex-direction: column; gap: 10px; font-variant-numeric: tabular-nums">
<sc-for list="{{reconcil}}" as="r" hint-placeholder-count="3">
<div role="row" style="display: grid; grid-template-columns: 180px minmax(0, 1fr) 90px; gap: 12px; align-items: center">
<span role="rowheader" style="font-size: 13px; font-weight: 500">{{r.label}}</span>
<span role="cell" style="display: flex; align-items: center; gap: 10px"><span style="height: 16px; width: {{r.w}}%; background: {{r.color}}; border-radius: 0 4px 4px 0"></span><span style="font-size: 13px; font-weight: 600; white-space: nowrap">{{r.value}}</span></span>
<span role="cell" style="text-align: right; font-size: 13px; color: {{r.diffColor}}; font-weight: 600">{{r.diff}}</span>
</div>
</sc-for>
</div>
</section>
'''

SCRIPT = r'''class Component extends DCLogic {
  renderVals() {
    const nf = (n) => Math.round(n).toLocaleString('fr-FR').replace(/[  ]/g, ' ');
    const pct = (x) => x.toFixed(1).replace('.', ',') + ' %';

    const flow = [
      { label: 'Demandées', n: 3113431, color: '#86B6EF', note: 'Demandes envoyées au partenaire d’impression' },
      { label: 'Imprimées et expédiées', n: 3101590, color: '#2A78D6', note: '99,6 % des demandes' },
      { label: 'Livrées', n: 1770796, color: '#104281', note: '57,1 % des cartes expédiées' }
    ].map((f) => ({ label: f.label, color: f.color, note: f.note, value: nf(f.n), w: (f.n / 3113431 * 80).toFixed(1), tip: f.label + ' : ' + nf(f.n) }));

    const regs = [
      ['Grand Lomé', 975000, 690000], ['Plateaux', 563000, 300000], ['Savanes', 423590, 188796],
      ['Maritime', 486000, 268000], ['Kara', 362000, 176000], ['Centrale', 292000, 148000]
    ];
    const rem = regs.map((r) => ({ name: r[0], n: r[1] - r[2], part: (r[1] - r[2]) / r[1] * 100 })).sort((a, b) => b.n - a.n);
    const maxRem = Math.max.apply(null, rem.map((r) => r.n));
    const byRegion = rem.map((r) => ({
      name: r.name, value: nf(r.n), part: pct(r.part), w: (r.n / maxRem * 72).toFixed(1),
      weight: r.part >= 50 ? '600' : '400', tip: r.name + ' : ' + nf(r.n) + ' cartes à remettre, ' + pct(r.part) + ' des cartes expédiées'
    }));

    const ageData = [['Moins de 30 jours', 96200, '#86B6EF'], ['30 à 90 jours', 268400, '#5598E7'], ['90 à 180 jours', 402600, '#1C5CAB'], ['Plus de 180 jours', 563594, '#104281']];
    const maxAge = Math.max.apply(null, ageData.map((a) => a[1]));
    const ages = ageData.map((a) => ({ label: a[0], value: nf(a[1]), color: a[2], w: (a[1] / maxAge * 75).toFixed(1), tip: a[0] + ' : ' + nf(a[1]) + ' cartes' }));

    const c = [
      ['EPP Doumassesse I G/B', 'Golfe, Grand Lomé', 44370, 31289],
      ['CEG Baguida Centre, Port de pêche', 'Golfe, Grand Lomé', 16033, 11818],
      ['EPP Worgou G/A', 'Tône, Savanes', 12411, null],
      ['EPP Gbetsogbe, Port autonome', 'Golfe, Grand Lomé', 12115, 9584],
      ['Lycée Nassable', 'Tône, Savanes', 10097, 6599],
      ['Hedzranawoe (Marché)', 'Golfe, Grand Lomé', null, 6208]
    ];
    const centres = c.map((x) => {
      const has = x[2] !== null && x[3] !== null;
      const p = has ? x[3] / x[2] * 100 : 0;
      return {
        name: x[0], place: x[1],
        exp: x[2] === null ? '\u2014' : nf(x[2]), liv: x[3] === null ? '\u2014' : nf(x[3]),
        expColor: x[2] === null ? '#4B5A6E' : '#071B35', livColor: x[3] === null ? '#4B5A6E' : '#071B35',
        hasPart: has, noPart: !has, part: pct(p), w: p.toFixed(1),
        missing: x[2] === null ? 'Absent du classement des cartes expédiées' : 'Absent du classement des cartes livrées'
      };
    });

    const rec = [['NIU générés', 3058886, '#B4BFCB', ''], ['Demandes d’impression', 3113431, '#2A78D6', '+' + nf(54545)], ['Cartes imprimées', 3101590, '#1C5CAB', '+' + nf(42704)]];
    const reconcil = rec.map((r) => ({ label: r[0], value: nf(r[1]), color: r[2], w: (r[1] / 3113431 * 78).toFixed(1), diff: r[3], diffColor: '#071B35' }));

    return { flow: flow, byRegion: byRegion, ages: ages, centres: centres, reconcil: reconcil };
  }
}'''

FOOTER = 'Maquette v3. Les totaux de cartes et les classements par centre viennent du BI actuel (données au 14/01/2026). Les régions et l’ancienneté des cartes à remettre sont fictives.'


def build():
    return page('Cartes e-ID', 'Cartes.dc.html', FILTERS, BODY, SCRIPT, 2000, FOOTER)

# ---------- v3.1 : carte interactive du Togo ----------
import re
import common_map as CM

REGION_SECTION = '''<section aria-labelledby="parregion" style="flex: 1 1 640px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 14px">
<div>
<h2 id="parregion" style="''' + H2 + '''">Cartes à remettre par région</h2>
<p style="''' + SUB + '''">Couleur : part des cartes expédiées qui restent à remettre. Barre : nombre de cartes. Choisissez une région pour afficher ses préfectures.</p>
</div>
''' + CM.block('map', 440, CM.legend('Part des cartes expédiées à remettre', ['&lt; 35 %', '35 à 45 %', '45 à 52 %', '52 % et +']), aside_w=230) + '''</section>'''

BODY, _n = re.subn(r'<section aria-labelledby="parregion".*?</section>', lambda m: REGION_SECTION, BODY, count=1, flags=re.S)
assert _n == 1
BODY = BODY.replace('<section aria-labelledby="anciennete" style="flex: 1 1 420px;', '<section aria-labelledby="anciennete" style="flex: 1 1 480px;')
BODY = BODY.replace('''<div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: stretch">

''' + REGION_SECTION, '''<div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: flex-start">

''' + REGION_SECTION)
assert '<div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: flex-start">' in BODY

_old = SCRIPT[SCRIPT.index('    const regs = ['):SCRIPT.index('    const ageData')]
_new = r'''    const st = this.state || {};
    const sel = st.region || null;
    const regs = [
      ['DAGL', 'Grand Lomé', 975000, 690000], ['PLA', 'Plateaux', 563000, 300000], ['SAV', 'Savanes', 423590, 188796],
      ['MAR', 'Maritime', 486000, 268000], ['KAR', 'Kara', 362000, 176000], ['CEN', 'Centrale', 292000, 148000]
    ];
    const rem = regs.map((r) => ({ id: r[0], name: r[1], n: r[2] - r[3], part: (r[2] - r[3]) / r[2] * 100 })).sort((a, b) => b.n - a.n);
    const maxRem = Math.max.apply(null, rem.map((r) => r.n));
    const byRegion = rem.map((r) => ({
      name: r.name, value: nf(r.n), part: pct(r.part), w: (r.n / maxRem * 72).toFixed(1),
      weight: r.part >= 50 ? '600' : '400', bg: sel === r.id ? '#EEF5FD' : 'transparent',
      tip: r.name + ' : ' + nf(r.n) + ' cartes à remettre, ' + pct(r.part) + ' des cartes expédiées'
    }));
    const R = ''' + CM.PREFS_JS + r''';
    const partByName = {}, nByName = {}, delaiByName = {}, prefIndex = {}, regOfPref = {};
    rem.forEach((r) => { partByName[r.name] = r.part; nByName[r.name] = r.n; });
    const natRem = regs.reduce((a, r) => a + r[2] - r[3], 0), natExp = regs.reduce((a, r) => a + r[2], 0);
    R.forEach((r) => {
      let n = 0, d = 0;
      r.prefs.forEach((p) => { n += p[1]; d += p[1] * p[4]; prefIndex[p[0]] = p; regOfPref[p[0]] = r.name; });
      delaiByName[r.name] = d / n;
    });
    const prefPart = (n) => { const reg = regOfPref[n]; return Math.max(5, Math.min(95, partByName[reg] * (1 + 0.04 * (prefIndex[n][4] - delaiByName[reg])))); };
    const map = this.buildMap({
      sel: sel, hover: st.mapHover || null,
      classes: [[35, '#B7D3F6'], [45, '#6DA7EC'], [52, '#2A78D6'], [101, '#184F95']],
      regionValue: (n) => partByName[n],
      prefValue: (n) => prefPart(n),
      onPick: (id) => this.setState({ region: id, mapHover: null }),
      onHover: (n) => this.setState({ mapHover: n }),
      describe: (n, isPref) => isPref
        ? n + ' : environ ' + pct(prefPart(n)) + ' des cartes expédiées restent à remettre'
        : n + ' : ' + nf(nByName[n]) + ' cartes à remettre, ' + pct(partByName[n]) + ' des cartes expédiées',
      national: 'Togo : ' + nf(natRem) + ' cartes à remettre, ' + pct(natRem / natExp * 100) + ' des cartes expédiées',
      px: 440, ar: 0.95, fmt: (v) => pct(v), nationalValue: pct(natRem / natExp * 100),
      bar: (n) => n ? { w: (nByName[n] / maxRem * 42).toFixed(1), sub: nf(nByName[n]) } : { w: '0', sub: nf(natRem) + ' cartes' }
    });
'''
SCRIPT = SCRIPT.replace(_old, _new).replace('    return { flow: flow, byRegion: byRegion,', '    return { map: map, flow: flow, byRegion: byRegion,')
assert 'return { map: map, flow' in SCRIPT
SCRIPT = CM.inject(SCRIPT)
FOOTER = FOOTER + ' Contours : geoBoundaries, d’après OpenStreetMap.'
