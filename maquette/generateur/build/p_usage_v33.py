from common import *

FILTERS = PERIODE + REGION + DIVIDER \
    + select('Type d’authentification', ['Tous les types', 'Biométrique (BIO)', 'Code à usage unique (OTP)', 'Démographique (DEMO)', 'Combinée (MULTIPLE)'], min_w=210) \
    + select('Partenaire', ['Tous les partenaires', 'Atos'], min_w=170)

ICON_OK = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: #2A78D6; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round"><circle cx="12" cy="12" r="10"></circle><polyline points="8 12.5 11 15.5 16 9.5"></polyline></svg>'
ICON_KO = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: #D03B3B; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round"><circle cx="12" cy="12" r="10"></circle><line x1="9" y1="9" x2="15" y2="15"></line><line x1="15" y1="9" x2="9" y2="15"></line></svg>'

BODY = title('Usage de l’identité : authentifications') + '''
<section aria-labelledby="echecs" style="position: relative; background: #FFFFFF; border-radius: 8px; padding: 36px 40px; box-sizing: border-box; display: flex; flex-wrap: wrap; gap: 24px 56px; align-items: center">
''' + BRACKETS + '''<div style="flex: 1 1 360px; display: flex; flex-direction: column; gap: 6px">
<h2 id="echecs" style="margin: 0; font-size: 15px; font-weight: 500; color: #4B5A6E">Authentifications échouées</h2>
<span style="font-size: clamp(40px, 9vw, 56px); font-weight: 600; letter-spacing: -0.02em; line-height: 1.05">57,7 %</span>
<p style="margin: 4px 0 0; font-size: 15px">294 763 échecs sur 510 499 requêtes. Toutes viennent d’un seul partenaire, Atos.</p>
<p style="margin: 0; font-size: 13px; color: #4B5A6E">Le BI actuel ne donne pas la cause des échecs : il faut exposer les codes d’erreur d’authentification.</p>
</div>
<div style="flex: 2 1 520px; min-width: 0; display: flex; flex-direction: column; gap: 12px">
<div role="img" aria-label="Réussies 42,3 %, échouées 57,7 %" style="display: flex; gap: 2px; height: 18px; border-radius: 4px; overflow: hidden">
<div style="width: 42.26%; background: #2A78D6"></div>
<div style="width: 57.74%; background: #D03B3B"></div>
</div>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px 24px">
<div style="display: flex; flex-direction: column; gap: 2px">
<span style="display: inline-flex; align-items: center; gap: 8px; font-size: 13px; color: #4B5A6E">''' + ICON_OK + '''Réussies</span>
<span style="font-size: 22px; font-weight: 600">215 736</span>
<span style="font-size: 13px; color: #4B5A6E">42,3 % des requêtes</span>
</div>
<div style="display: flex; flex-direction: column; gap: 2px">
<span style="display: inline-flex; align-items: center; gap: 8px; font-size: 13px; color: #4B5A6E">''' + ICON_KO + '''Échouées</span>
<span style="font-size: 22px; font-weight: 600">294 763</span>
<span style="font-size: 13px; color: #4B5A6E">57,7 % des requêtes</span>
</div>
<div style="display: flex; flex-direction: column; gap: 2px">
<span style="font-size: 13px; color: #4B5A6E">Dernière requête</span>
<span style="font-size: 22px; font-weight: 600">14/01/2026</span>
<span style="font-size: 13px; color: #4B5A6E">à 11h05</span>
</div>
</div>
</div>
</section>

<div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: stretch">

<section aria-labelledby="types" style="flex: 1 1 560px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 10px">
<div>
<h2 id="types" style="''' + H2 + '''">Par type d’authentification</h2>
<p style="''' + SUB + '''">Volume de requêtes et part d’échecs pour chaque type.</p>
</div>
<div style="overflow-x: auto">
<div role="table" aria-label="Authentifications par type" style="min-width: 520px; font-variant-numeric: tabular-nums">
<div role="row" style="display: grid; grid-template-columns: minmax(150px, 1fr) minmax(170px, 1.3fr) 64px minmax(150px, 1fr); gap: 12px; padding: 6px 0; font-size: 12px; color: #4B5A6E">
<span role="columnheader">Type</span><span role="columnheader">Requêtes</span><span role="columnheader" style="text-align: right">Part</span><span role="columnheader">Échecs</span>
</div>
<sc-for list="{{types}}" as="t" hint-placeholder-count="4">
<div role="row" style="display: grid; grid-template-columns: minmax(150px, 1fr) minmax(170px, 1.3fr) 64px minmax(150px, 1fr); gap: 12px; align-items: center; padding: 10px 0; border-top: 1px solid #EEF2F5">
<span role="rowheader" style="display: flex; flex-direction: column"><span style="font-weight: 500">{{t.label}}</span><span style="font-size: 12px; color: #4B5A6E">{{t.code}}</span></span>
<span role="cell" style="display: flex; align-items: center; gap: 8px"><span style="height: 12px; width: {{t.w}}%; min-width: 2px; background: #2A78D6; border-radius: 0 4px 4px 0"></span><span style="white-space: nowrap">{{t.value}}</span></span>
<span role="cell" style="text-align: right">{{t.share}}</span>
<span role="cell" style="display: flex; align-items: center; gap: 8px"><span style="flex-grow: 1; max-width: 90px; height: 10px; background: #EEF2F5; border-radius: 0 4px 4px 0"><span style="display: block; height: 10px; width: {{t.failW}}%; background: #D03B3B; border-radius: 0 4px 4px 0"></span></span><span style="font-weight: {{t.failWeight}}; white-space: nowrap">{{t.fail}}</span></span>
</div>
</sc-for>
</div>
</div>
<p style="margin: auto 0 0; font-size: 12px; color: #4B5A6E">Le BI actuel ne montre que la part de chaque type (biométrique ≈ 96 %) ; le détail des échecs par type est à construire.</p>
</section>

<section aria-labelledby="causes" style="flex: 1 1 440px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 12px">
<div>
<h2 id="causes" style="''' + H2 + '''">Causes des échecs</h2>
<p style="''' + SUB + '''">Regroupement proposé des codes d’erreur d’authentification, à brancher sur la base IDA.</p>
</div>
<sc-for list="{{causes}}" as="c" hint-placeholder-count="5">
<div title="{{c.tip}}" style="display: grid; grid-template-columns: minmax(0, 1fr) 56px; gap: 4px 12px; align-items: center">
<span style="font-size: 13px">{{c.label}}</span>
<span style="font-size: 13px; color: #4B5A6E; text-align: right; font-variant-numeric: tabular-nums">{{c.pct}}</span>
<span style="display: flex; align-items: center; gap: 8px; grid-column: 1 / 3"><span style="height: 12px; width: {{c.w}}%; background: #2A78D6; border-radius: 0 4px 4px 0"></span><span style="font-size: 13px; font-weight: 600; white-space: nowrap; font-variant-numeric: tabular-nums">{{c.value}}</span></span>
</div>
</sc-for>
</section>

</div>

<div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: stretch">

<section aria-labelledby="semaines" style="flex: 2 1 620px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 14px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 8px 24px">
<div>
<h2 id="semaines" style="''' + H2 + '''">Requêtes par semaine</h2>
<p style="''' + SUB + '''">12 dernières semaines complètes. Survolez une semaine pour le détail.</p>
</div>
<div style="display: flex; gap: 18px; font-size: 13px; color: #4B5A6E">
<span style="display: inline-flex; align-items: center; gap: 8px"><span aria-hidden="true" style="width: 12px; height: 12px; border-radius: 3px; background: #2A78D6"></span>Réussies</span>
<span style="display: inline-flex; align-items: center; gap: 8px"><span aria-hidden="true" style="width: 12px; height: 12px; border-radius: 3px; background: #D03B3B"></span>Échouées</span>
</div>
</div>
<p aria-live="polite" style="margin: 0; padding: 8px 12px; border-radius: 6px; background: #F1F4F6; font-size: 13px">{{readout}}</p>
<div style="overflow-x: auto; padding-top: 10px">
<div style="min-width: 560px; display: flex; gap: 10px">
<div aria-hidden="true" style="position: relative; width: 48px; height: 200px; font-size: 12px; color: #4B5A6E; font-variant-numeric: tabular-nums; flex-shrink: 0">
<span style="position: absolute; right: 0; top: -9px">15 000</span>
<span style="position: absolute; right: 0; top: 58px">10 000</span>
<span style="position: absolute; right: 0; top: 124px">5 000</span>
<span style="position: absolute; right: 0; top: 191px">0</span>
</div>
<div style="flex-grow: 1; min-width: 0">
<div style="position: relative; height: 200px; border-bottom: 1px solid #9AA7B5; background-image: linear-gradient(#E6EBEF 1px, transparent 1px); background-size: 100% 66.67px">
<div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; display: flex; align-items: flex-end">
<sc-for list="{{weeks}}" as="w" hint-placeholder-count="12">
<button type="button" onMouseEnter="{{w.enter}}" onFocus="{{w.enter}}" aria-label="{{w.aria}}" style="flex: 1 1 0; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 2px; padding: 0; border: 0; background: {{w.band}}; cursor: default">
<span style="width: 22px; height: {{w.hKo}}px; background: #D03B3B; border-radius: 4px 4px 0 0"></span>
<span style="width: 22px; height: {{w.hOk}}px; background: #2A78D6"></span>
</button>
</sc-for>
</div>
</div>
<div aria-hidden="true" style="display: flex; margin-top: 6px; font-size: 12px; color: #4B5A6E; font-variant-numeric: tabular-nums">
<sc-for list="{{weeks}}" as="w" hint-placeholder-count="12">
<span style="flex: 1 1 0; text-align: center">{{w.label}}</span>
</sc-for>
</div>
</div>
</div>
</div>
</section>

<section aria-labelledby="partenaire" style="flex: 1 1 340px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 12px">
<div>
<h2 id="partenaire" style="''' + H2 + '''">Partenaire raccordé</h2>
<p style="''' + SUB + '''">Un seul partenaire envoie des requêtes : une fiche remplace le classement des 5 premiers.</p>
</div>
<div style="padding: 18px; border: 1px solid #DCE3E9; border-radius: 6px; display: flex; flex-direction: column; gap: 10px">
<span style="font-size: 18px; font-weight: 600">Atos</span>
<div role="table" aria-label="Requêtes du partenaire Atos" style="display: flex; flex-direction: column; gap: 6px; font-variant-numeric: tabular-nums">
<div role="row" style="display: flex; justify-content: space-between; gap: 12px; font-size: 14px"><span role="rowheader" style="color: #4B5A6E">Requêtes</span><span role="cell" style="font-weight: 600">510 499</span></div>
<div role="row" style="display: flex; justify-content: space-between; gap: 12px; font-size: 14px"><span role="rowheader" style="display: inline-flex; align-items: center; gap: 6px; color: #4B5A6E">''' + ICON_OK + '''Réussies</span><span role="cell" style="font-weight: 600">215 736</span></div>
<div role="row" style="display: flex; justify-content: space-between; gap: 12px; font-size: 14px"><span role="rowheader" style="display: inline-flex; align-items: center; gap: 6px; color: #4B5A6E">''' + ICON_KO + '''Échouées</span><span role="cell" style="font-weight: 600">294 763</span></div>
<div role="row" style="display: flex; justify-content: space-between; gap: 12px; font-size: 14px; padding-top: 8px; border-top: 1px solid #EEF2F5"><span role="rowheader" style="color: #4B5A6E">Part du total</span><span role="cell" style="font-weight: 600">100 %</span></div>
</div>
</div>
<p style="margin: auto 0 0; font-size: 12px; color: #4B5A6E">Quand d’autres partenaires (banques, opérateurs, administrations) seront raccordés, cette fiche deviendra un tableau comparatif.</p>
</section>

</div>
'''

SCRIPT = r'''class Component extends DCLogic {
  renderVals() {
    const st = this.state || {};
    const nf = (n) => Math.round(n).toLocaleString('fr-FR').replace(/[  ]/g, ' ');
    const pct = (x) => x.toFixed(1).replace('.', ',') + ' %';
    const TOTAL = 510499;

    const T = [
      ['Biométrique', 'BIO', 490080, 290300], ['Code à usage unique', 'OTP', 18380, 3860],
      ['Démographique', 'DEMO', 1290, 390], ['Combinée', 'MULTIPLE', 749, 213]
    ];
    const types = T.map((t) => {
      const f = t[3] / t[2] * 100;
      return { label: t[0], code: t[1], value: nf(t[2]), share: pct(t[2] / TOTAL * 100), w: (t[2] / 490080 * 70).toFixed(1), fail: pct(f), failW: f.toFixed(1), failWeight: f >= 50 ? '600' : '400' };
    });

    const C = [
      ['Empreinte non concordante', 168400], ['Qualité de capture insuffisante', 71200],
      ['NIU ou identifiant virtuel invalide ou inactif', 29800], ['Code OTP expiré ou erroné', 3860], ['Autres causes', 21503]
    ];
    const FAIL = 294763;
    const causes = C.map((c) => ({ label: c[0], value: nf(c[1]), pct: pct(c[1] / FAIL * 100), w: (c[1] / 168400 * 75).toFixed(1), tip: c[0] + ' : ' + nf(c[1]) + ' échecs' }));

    const W = [
      ['20/10', '20 octobre', 9800, 0.55], ['27/10', '27 octobre', 10400, 0.56], ['03/11', '3 novembre', 11200, 0.57],
      ['10/11', '10 novembre', 11900, 0.58], ['17/11', '17 novembre', 11500, 0.57], ['24/11', '24 novembre', 12300, 0.58],
      ['01/12', '1er décembre', 12800, 0.59], ['08/12', '8 décembre', 12100, 0.58], ['15/12', '15 décembre', 8100, 0.60],
      ['22/12', '22 décembre', 6900, 0.61], ['29/12', '29 décembre', 9200, 0.58], ['05/01', '5 janvier', 9600, 0.59]
    ];
    const hov = typeof st.hover === 'number' ? st.hover : W.length - 1;
    const H = 200, MAX = 15000;
    const weeks = W.map((w, i) => {
      const ko = Math.round(w[2] * w[3]), ok = w[2] - ko;
      return {
        label: w[0], hOk: (ok / MAX * H).toFixed(1), hKo: (ko / MAX * H - 2).toFixed(1),
        band: i === hov ? 'rgba(42,120,214,0.07)' : 'transparent',
        aria: 'Semaine du ' + w[1] + ' : ' + nf(w[2]) + ' requêtes, dont ' + nf(ko) + ' échouées',
        enter: () => this.setState({ hover: i })
      };
    });
    const hw = W[hov];
    const hko = Math.round(hw[2] * hw[3]);
    const readout = 'Semaine du ' + hw[1] + ' : ' + nf(hw[2]) + ' requêtes, ' + nf(hw[2] - hko) + ' réussies et ' + nf(hko) + ' échouées (' + pct(hw[3] * 100) + ').';

    return { types: types, causes: causes, weeks: weeks, readout: readout };
  }
}'''

FOOTER = 'Maquette v3. Les totaux d’authentification, la part des types et le partenaire viennent du BI actuel (données au 14/01/2026). Le détail des échecs par type, les causes et l’évolution hebdomadaire sont fictifs.'


def build():
    return page('Usage de l’identité', 'Usage.dc.html', FILTERS, BODY, SCRIPT, 1540, FOOTER)
