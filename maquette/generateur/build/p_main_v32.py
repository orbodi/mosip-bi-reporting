from common import *

FILTERS = PERIODE + REGION

BODY = title('Vue d’ensemble du parcours citoyen') + '''
<section aria-labelledby="parcours" style="position: relative; background: #FFFFFF; border-radius: 8px; padding: 36px 40px; box-sizing: border-box; display: flex; flex-direction: column; gap: 22px">
''' + BRACKETS + '''<div style="max-width: 820px">
<h2 id="parcours" style="margin: 0; font-size: 22px; font-weight: 600; letter-spacing: -0.01em">Du rendez-vous à la carte en main</h2>
<p style="margin: 6px 0 0; font-size: 15px">Sur 3 278 239 inscrits, 1 770 796 ont reçu leur carte. La remise des cartes est l’étape qui retient le plus de citoyens.</p>
</div>
<div style="overflow-x: auto">
<div role="list" style="min-width: 780px; display: grid; grid-template-columns: repeat(6, minmax(0, 1fr))">
<sc-for list="{{steps}}" as="s" hint-placeholder-count="6">
<div role="listitem" style="display: flex; flex-direction: column; gap: 6px; padding: 0 16px; border-left: {{s.sep}}">
<span style="font-size: 13px; font-weight: 500; color: #4B5A6E; min-height: 40px">{{s.label}}</span>
<span style="font-size: 22px; font-weight: 600; white-space: nowrap">{{s.value}}</span>
<div aria-hidden="true" style="height: 150px; display: flex; align-items: flex-end; border-bottom: 1px solid #9AA7B5">
<div title="{{s.tip}}" style="width: 48px; height: {{s.h}}px; background: {{s.color}}; border-radius: 4px 4px 0 0"></div>
</div>
<span style="display: flex; gap: 6px; align-items: flex-start; font-size: 13px; color: #071B35; font-weight: {{s.noteWeight}}">
<sc-if value="{{s.warn}}" hint-placeholder-val="{{false}}"><svg width="14" height="14" viewBox="0 0 24 24" aria-label="Alerte" style="flex-shrink: 0; margin-top: 3px; fill: #EC835A; stroke: none"><path d="M12 2 1 21h22L12 2z"></path></svg></sc-if>
<span>{{s.note}}</span>
</span>
</div>
</sc-for>
</div>
</div>
</section>

<div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: flex-start">

<section aria-labelledby="traiter" style="flex: 1 1 520px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column">
<h2 id="traiter" style="''' + H2 + '''; margin-bottom: 8px">À traiter</h2>
<ul style="list-style: none; margin: 0; padding: 0">
<sc-for list="{{alerts}}" as="a" hint-placeholder-count="4">
<li style="display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 16px; align-items: center; padding: 14px 0; border-top: 1px solid #E6EBEF">
<div style="display: flex; flex-direction: column; gap: 2px; min-width: 0">
<span style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600"><svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="fill: {{a.color}}; stroke: none"><path d="M12 2 1 21h22L12 2z"></path></svg>{{a.level}}, {{a.module}}</span>
<span style="font-size: 15px; font-weight: 600">{{a.title}}</span>
<span style="font-size: 13px; color: #4B5A6E">{{a.detail}}</span>
</div>
<a href="{{a.href}}" style="display: inline-flex; align-items: center; min-height: 44px; font-size: 13px; font-weight: 600; white-space: nowrap">{{a.cta}}</a>
</li>
</sc-for>
</ul>
</section>

<section aria-label="Indicateurs clés" style="flex: 1 1 440px; min-width: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1px; background: #DCE3E9; border-radius: 8px; overflow: hidden">
<sc-for list="{{tiles}}" as="t" hint-placeholder-count="4">
<div style="background: #FFFFFF; padding: 22px 24px; display: flex; flex-direction: column; gap: 4px">
<h2 style="margin: 0; font-size: 13px; font-weight: 500; color: #4B5A6E">{{t.label}}</h2>
<span style="font-size: 30px; font-weight: 600; letter-spacing: -0.01em; line-height: 1.2">{{t.value}}</span>
<span style="font-size: 13px; color: #4B5A6E">{{t.detail}}</span>
<a href="{{t.href}}" style="margin-top: auto; padding-top: 8px; font-size: 13px; font-weight: 600">{{t.cta}}</a>
</div>
</sc-for>
</section>

</div>

<section aria-labelledby="regions" style="''' + CARD + '''; display: flex; flex-direction: column; gap: 8px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 4px 24px">
<div>
<h2 id="regions" style="''' + H2 + '''">Le parcours par région</h2>
<p style="''' + SUB + '''">Part des inscrits qui ont reçu leur carte : de 41,9 % en Savanes à 67,6 % dans le Grand Lomé.</p>
</div>
<a href="Enrolement.dc.html" style="display: inline-flex; align-items: center; min-height: 44px; font-size: 13px; font-weight: 600">Explorer le territoire</a>
</div>
<div style="overflow-x: auto">
<div role="table" aria-label="Parcours par région" style="min-width: 760px; font-variant-numeric: tabular-nums">
<div role="row" style="display: grid; grid-template-columns: minmax(130px, 1fr) 110px 110px 110px minmax(240px, 2fr) 80px; gap: 16px; padding: 6px 0; font-size: 12px; color: #4B5A6E">
<span role="columnheader">Région</span><span role="columnheader" style="text-align: right">Inscriptions</span><span role="columnheader" style="text-align: right">NIU générés</span><span role="columnheader" style="text-align: right">Cartes livrées</span><span role="columnheader">Inscrits ayant reçu leur carte</span><span role="columnheader" style="text-align: right">Rejets</span>
</div>
<sc-for list="{{regions}}" as="r" hint-placeholder-count="6">
<div role="row" style="display: grid; grid-template-columns: minmax(130px, 1fr) 110px 110px 110px minmax(240px, 2fr) 80px; gap: 16px; align-items: center; padding: 10px 0; border-top: 1px solid #EEF2F5">
<span role="rowheader" style="font-weight: 500">{{r.name}}</span>
<span role="cell" style="text-align: right">{{r.inscr}}</span>
<span role="cell" style="text-align: right">{{r.niu}}</span>
<span role="cell" style="text-align: right">{{r.liv}}</span>
<span role="cell" style="display: flex; align-items: center; gap: 10px">
<span style="flex-grow: 1; height: 12px; background: #EEF2F5; border-radius: 0 4px 4px 0"><span style="display: block; height: 12px; width: {{r.w}}%; background: #2A78D6; border-radius: 0 4px 4px 0"></span></span>
<span style="width: 52px; text-align: right; font-weight: {{r.cardWeight}}">{{r.part}}</span>
</span>
<span role="cell" style="text-align: right">{{r.rej}}</span>
</div>
</sc-for>
</div>
</div>
</section>
'''

SCRIPT = r'''class Component extends DCLogic {
  renderVals() {
    const nf = (n) => Math.round(n).toLocaleString('fr-FR').replace(/[  ]/g, ' ');
    const pct = (x) => x.toFixed(1).replace('.', ',') + ' %';
    const MAX = 3278239, H = 140;
    const steps = [
      { label: 'Pré-inscriptions', n: 606850, color: '#B4BFCB', note: 'Facultative ; équivaut à 18,5 % des inscriptions' },
      { label: 'Inscriptions', n: 3278239, color: '#86B6EF', note: 'Base du parcours' },
      { label: 'NIU générés', n: 3058886, color: '#5598E7', note: '93,3 % des inscriptions' },
      { label: 'Cartes demandées', n: 3113431, color: '#2A78D6', note: '101,8 % des NIU, à réconcilier' },
      { label: 'Cartes expédiées', n: 3101590, color: '#1C5CAB', note: '99,6 % des demandes' },
      { label: 'Cartes livrées', n: 1770796, color: '#104281', note: '57,1 % des expédiées : ' + nf(1330794) + ' cartes à remettre', warn: true }
    ].map((s, i) => ({
      label: s.label, value: nf(s.n), note: s.note, color: s.color, warn: !!s.warn,
      noteWeight: s.warn ? '600' : '400', h: (s.n / MAX * H).toFixed(1),
      sep: i === 0 ? 'none' : '1px solid #E6EBEF', tip: s.label + ' : ' + nf(s.n)
    }));

    const alerts = [
      { level: 'Critique', module: 'usage', color: '#D03B3B', title: '57,7 % des authentifications échouent',
        detail: nf(294763) + ' échecs sur ' + nf(510499) + ' requêtes, toutes venant d’un seul partenaire.', cta: 'Analyser les échecs', href: 'Usage.dc.html' },
      { level: 'Priorité élevée', module: 'cartes', color: '#EC835A', title: nf(1330794) + ' cartes expédiées non remises',
        detail: '42,9 % des cartes expédiées n’ont pas encore été livrées.', cta: 'Voir les cartes à remettre', href: 'Cartes.dc.html' },
      { level: 'Priorité élevée', module: 'enrôlement', color: '#EC835A', title: nf(118402) + ' paquets bloqués depuis plus de 30 jours',
        detail: '47 % attendent une vérification manuelle.', cta: 'Voir les blocages', href: 'Technique.dc.html' },
      { level: 'À surveiller', module: 'qualité', color: '#FAB219', title: 'Trois compteurs du BI actuel sont faux',
        detail: 'Synchronisés négatifs, pré-inscriptions réservées à zéro, plus de cartes que de NIU.', cta: 'Voir les contrôles', href: 'Technique.dc.html' }
    ];

    const tiles = [
      { label: 'Délai médian, de l’inscription au NIU', value: '6,5 jours', detail: '90 % des NIU en moins de 14 jours', cta: 'Détail de l’enrôlement', href: 'Enrolement.dc.html' },
      { label: 'Délai médian, du NIU à la carte remise', value: '34 jours', detail: 'Indicateur à créer à partir des dates de livraison', cta: 'Détail des cartes', href: 'Cartes.dc.html' },
      { label: 'Authentifications réussies', value: '42,3 %', detail: nf(215736) + ' sur ' + nf(510499) + ' requêtes', cta: 'Détail de l’usage', href: 'Usage.dc.html' },
      { label: 'Mises à jour et récupérations', value: nf(14740), detail: nf(12689) + ' mises à jour, ' + nf(2051) + ' récupérations de NIU', cta: 'Détail de l’enrôlement', href: 'Enrolement.dc.html' }
    ];

    const regs = [
      ['Grand Lomé', 1020000, 960432, 690000, 2.1], ['Plateaux', 598000, 556198, 300000, 2.8], ['Maritime', 512000, 478964, 268000, 2.5],
      ['Savanes', 450239, 412740, 188796, 3.6], ['Kara', 386000, 358098, 176000, 2.9], ['Centrale', 312000, 288552, 148000, 3.1]
    ];
    const regions = regs.map((r) => {
      const part = r[3] / r[1] * 100;
      return { name: r[0], inscr: nf(r[1]), niu: nf(r[2]), liv: nf(r[3]), part: pct(part), w: part.toFixed(1), rej: pct(r[4]), cardWeight: part < 45 ? '600' : '400' };
    });

    return { steps: steps, alerts: alerts, tiles: tiles, regions: regions };
  }
}'''

FOOTER = 'Maquette v3. Les totaux nationaux (inscriptions, NIU, cartes, authentifications, pré-inscriptions) viennent du BI actuel, avec des données au 14/01/2026. Les délais, les régions et les cartes livrées par région sont fictifs.'


def build():
    return page('Vue d’ensemble du parcours citoyen', 'Main.dc.html', FILTERS, BODY, SCRIPT, 2280, FOOTER)

# ---------- v3.1 : carte interactive du Togo ----------
import re
import common_map as CM

REGIONS_SECTION = '''<section aria-labelledby="regions" style="''' + CARD + '''; display: flex; flex-direction: column; gap: 16px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 4px 24px">
<div>
<h2 id="regions" style="''' + H2 + '''">Le parcours par région</h2>
<p style="''' + SUB + '''">Part des inscrits qui ont reçu leur carte : de 41,9 % en Savanes à 67,6 % dans le Grand Lomé.</p>
</div>
<a href="Enrolement.dc.html" style="display: inline-flex; align-items: center; min-height: 44px; font-size: 13px; font-weight: 600">Explorer le territoire</a>
</div>
<div style="display: flex; flex-wrap: wrap; gap: 24px 32px; align-items: flex-start">
<div style="flex: 1 1 320px; max-width: 100%; min-width: 0; display: flex; flex-direction: column; gap: 10px">
''' + CM.readout('map') + CM.map_svg('map', 440) + CM.legend('Inscrits ayant reçu leur carte', ['&lt; 45 %', '45 à 50 %', '50 à 60 %', '60 % et +']) \
    + CM.region_buttons('mapButtons') + CM.ATTRIBUTION + '''</div>
<div style="flex: 2 1 600px; min-width: 0; overflow-x: auto">
<div role="table" aria-label="Parcours par région" style="min-width: 640px; font-variant-numeric: tabular-nums">
<div role="row" style="display: grid; grid-template-columns: minmax(110px, 1fr) 100px 100px 100px minmax(170px, 1.6fr) 64px; gap: 14px; padding: 6px 8px; font-size: 12px; color: #4B5A6E">
<span role="columnheader">Région</span><span role="columnheader" style="text-align: right">Inscriptions</span><span role="columnheader" style="text-align: right">NIU générés</span><span role="columnheader" style="text-align: right">Cartes livrées</span><span role="columnheader">Inscrits avec carte</span><span role="columnheader" style="text-align: right">Rejets</span>
</div>
<sc-for list="{{regions}}" as="r" hint-placeholder-count="6">
<div role="row" style="display: grid; grid-template-columns: minmax(110px, 1fr) 100px 100px 100px minmax(170px, 1.6fr) 64px; gap: 14px; align-items: center; padding: 10px 8px; border-top: 1px solid #EEF2F5; background: {{r.bg}}; border-radius: 4px">
<span role="rowheader" style="font-weight: {{r.nameWeight}}">{{r.name}}</span>
<span role="cell" style="text-align: right">{{r.inscr}}</span>
<span role="cell" style="text-align: right">{{r.niu}}</span>
<span role="cell" style="text-align: right">{{r.liv}}</span>
<span role="cell" style="display: flex; align-items: center; gap: 10px">
<span style="flex-grow: 1; height: 12px; background: #E3EAF3; border-radius: 0 4px 4px 0"><span style="display: block; height: 12px; width: {{r.w}}%; background: #2A78D6; border-radius: 0 4px 4px 0"></span></span>
<span style="width: 52px; text-align: right; font-weight: {{r.cardWeight}}">{{r.part}}</span>
</span>
<span role="cell" style="text-align: right">{{r.rej}}</span>
</div>
</sc-for>
</div>
<div style="margin-top: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px">
<div style="padding: 16px 18px; border-radius: 6px; background: #F1F4F6; display: flex; flex-direction: column; gap: 4px">
<span style="font-size: 24px; font-weight: 600">25,7 points</span>
<span style="font-size: 13px; color: #4B5A6E">d’écart de remise des cartes entre le Grand Lomé (67,6 %) et les Savanes (41,9 %).</span>
</div>
<div style="padding: 16px 18px; border-radius: 6px; background: #F1F4F6; display: flex; flex-direction: column; gap: 4px">
<span style="font-size: 24px; font-weight: 600">39 %</span>
<span style="font-size: 13px; color: #4B5A6E">des cartes livrées l’ont été dans le Grand Lomé, qui ne compte que 31 % des inscriptions.</span>
</div>
<div style="padding: 16px 18px; border-radius: 6px; background: #F1F4F6; display: flex; flex-direction: column; gap: 4px">
<span style="font-size: 24px; font-weight: 600">3 régions</span>
<span style="font-size: 13px; color: #4B5A6E">sous la barre de 50 % d’inscrits ayant reçu leur carte : Savanes, Kara et Centrale.</span>
</div>
</div>
</div>
</div>
</section>'''

BODY, _n = re.subn(r'<section aria-labelledby="regions".*?</section>', lambda m: REGIONS_SECTION, BODY, count=1, flags=re.S)
assert _n == 1

_old_regs = SCRIPT[SCRIPT.index('    const regs = ['):SCRIPT.index('    return { steps: steps')]
_new_regs = r'''    const st = this.state || {};
    const sel = st.region || null;
    const regs = [
      ['DAGL', 'Grand Lomé', 1020000, 961080, 690000, 2.1], ['PLA', 'Plateaux', 598000, 555858, 300000, 2.8], ['MAR', 'Maritime', 512000, 478964, 268000, 2.5],
      ['SAV', 'Savanes', 450239, 412740, 188796, 3.6], ['KAR', 'Kara', 386000, 357964, 176000, 2.9], ['CEN', 'Centrale', 312000, 288370, 148000, 3.1]
    ];
    const regions = regs.map((r) => {
      const part = r[4] / r[2] * 100;
      const on = sel === r[0];
      return { name: r[1], inscr: nf(r[2]), niu: nf(r[3]), liv: nf(r[4]), part: pct(part), w: part.toFixed(1), rej: pct(r[5]),
        cardWeight: part < 45 ? '600' : '400', bg: on ? '#EEF5FD' : 'transparent', nameWeight: on ? '700' : '500' };
    });
    // Carte : part des inscrits ayant reçu leur carte (préfectures : estimation à partir du délai médian)
    const R = ''' + CM.PREFS_JS + r''';
    const partByName = {}, delaiByName = {}, prefIndex = {};
    regs.forEach((r) => { partByName[r[1]] = r[4] / r[2] * 100; });
    R.forEach((r) => {
      let n = 0, d = 0;
      r.prefs.forEach((p) => { n += p[1]; d += p[1] * p[4]; prefIndex[p[0]] = p; });
      delaiByName[r.name] = d / n;
    });
    const prefPart = (n, reg) => Math.max(5, Math.min(95, partByName[reg] * (1 - 0.04 * (prefIndex[n][4] - delaiByName[reg]))));
    const livByName = {};
    regs.forEach((r) => { livByName[r[1]] = r[4]; });
    const map = this.buildMap({
      sel: sel, hover: st.mapHover || null,
      classes: [[45, '#B7D3F6'], [50, '#6DA7EC'], [60, '#2A78D6'], [101, '#184F95']],
      regionValue: (n) => partByName[n],
      prefValue: (n, reg) => prefPart(n, reg),
      onPick: (id) => this.setState({ region: id, mapHover: null }),
      onHover: (n) => this.setState({ mapHover: n }),
      describe: (n, isPref) => {
        if (isPref) { const reg = Object.keys(partByName).find((k) => R.find((x) => x.name === k).prefs.some((p) => p[0] === n)); return n + ' : environ ' + pct(prefPart(n, reg)) + ' des inscrits ont reçu leur carte'; }
        return n + ' : ' + pct(partByName[n]) + ' des inscrits ont reçu leur carte (' + nf(livByName[n]) + ' cartes)';
      },
      national: 'Survolez une région pour voir ses chiffres ; cliquez pour afficher ses préfectures.'
    });
''' + CM.BUTTONS_JS
SCRIPT = SCRIPT.replace(_old_regs, _new_regs).replace('    return { steps: steps, alerts: alerts, tiles: tiles, regions: regions };',
                                                    '    return { steps: steps, alerts: alerts, tiles: tiles, regions: regions, map: map, mapButtons: mapButtons };')
assert 'mapButtons: mapButtons' in SCRIPT
SCRIPT = CM.inject(SCRIPT)
FOOTER = FOOTER + ' Contours : geoBoundaries, d’après OpenStreetMap.'
