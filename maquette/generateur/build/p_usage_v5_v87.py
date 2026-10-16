"""Authentifications v5 (8 oct. 2026) : refonte au langage des autres pages.

Chiffres repris de p_usage : totaux, part des types et partenaire du BI actuel (510 499 requêtes, 215 736 réussies,
294 763 échouées, Atos) ; échecs par type, causes et semaines restent illustratifs, comme avant.
- Bandeau : titre, pastille jaune « Dernière mise à jour : 14/01/2026 à 11h05 » à droite, filtres en pastilles.
- Requêtes d'authentification (crochets jaunes) : chiffre principal, barre réussies / échouées et 6 cartes v9.
- Par type et causes des échecs côte à côte ; requêtes par semaine et partenaire côte à côte.
"""
import json
from common import *
import p_usage as OLD, p_main_v3 as V3, p_enrol_v5 as EN, p_bio_v5 as V5, p_cartes_v5 as CA

nf, pct = V5.B.nf, V5.pct
_N, _G1, _G2, _IA = EN._N, EN._G1, EN._G2, EN._IA
IC = dict(V5.IC)
IC['idcard'] = CA.IC['idcard']
IC['otp'] = (f'<svg {_IA}><rect x="12" y="4" width="24" height="40" rx="4" fill="{_G1}"></rect><path d="M12 10h24M12 37h24M21 40.5h6"></path>'
             f'<rect x="16" y="17" width="16" height="10" rx="2" fill="{_G2}"></rect><path d="M20 22h.01M24 22h.01M28 22h.01" stroke-width="2.8"></path></svg>')
IC['partner'] = (f'<svg {_IA}><path d="M8 42V13l15-7v36" fill="{_G1}"></path><path d="M23 42V18h17v24" fill="{_G2}"></path>'
                 '<path d="M4 42h40M13 15v.01M18 15v.01M13 22v.01M18 22v.01M13 29v.01M18 29v.01M28 25h7M28 31h7" stroke-width="2.4"></path></svg>')
BLUE, RED = '#2A78D6', '#D03B3B'

TOTAL, OK, KO = 510499, 215736, 294763
assert OK + KO == TOTAL
TYPES = [('Biométrique', 'BIO', 490080, 290300), ('Code à usage unique', 'OTP', 18380, 3860),
         ('Démographique', 'DEMO', 1290, 390), ('Combinée', 'MULTIPLE', 749, 213)]
assert sum(t[2] for t in TYPES) == TOTAL and sum(t[3] for t in TYPES) == KO
CAUSES = [('Empreinte non concordante', 168400), ('Qualité de capture insuffisante', 71200),
          ('NIU ou identifiant virtuel invalide ou inactif', 29800), ('Code OTP expiré ou erroné', 3860), ('Autres causes', 21503)]
assert sum(c[1] for c in CAUSES) == KO


def scard(icon, label, value, detail):
    return (f'<div class="v9-card en-card">{IC[icon]}<span class="v9-body"><span class="v9-name">{label}</span>'
            f'<span class="v9-val">{value}</span><span class="v9-sub">{detail}</span></span></div>')


# =============== Bandeau ===============
TITLE = ('<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 14px">\n'
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px; align-self: stretch">'
         '<h1 style="margin: 0; font-size: 30px; font-weight: 600; letter-spacing: -0.015em; color: #FFFFFF">Authentifications</h1>'
         + EN.FRESH.replace('14/01/2026 à 11h42', '14/01/2026 à 11h05') + '</div>\n'
         '<form aria-label="Filtres appliqués à toute la page" style="display: flex; flex-wrap: wrap; gap: 10px">'
         + EN.pill('Période', ['Depuis le début', '7 derniers jours', '30 derniers jours', '90 derniers jours', 'Période personnalisée'], 150)
         + EN.pill('Région', ['Toutes les régions', 'Grand Lomé', 'Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'], 150)
         + EN.pill('Type', ['Tous les types', 'Biométrique (BIO)', 'Code à usage unique (OTP)', 'Démographique (DEMO)', 'Combinée (MULTIPLE)'], 120)
         + EN.pill('Partenaire', ['Tous', 'Atos'], 70)
         + '</form>\n</div>\n')
assert '14/01/2026 à 11h05' in TITLE

# =============== 1. Requêtes ===============
_demo = TYPES[2][2] + TYPES[3][2]
P1 = ('<section aria-labelledby="requetes" class="v7-panel en-dev">\n' + BRACKETS + EN.head('requetes', 'Requêtes d’authentification') +
      '<div class="en-pre">\n<div class="en-pre-main">'
      f'<p class="en-big"><span class="en-bigv">{nf(TOTAL)}</span><span class="en-bigu">requêtes de vérification d’identité reçues</span></p>'
      f'<div role="img" aria-label="Réussies {pct(OK / TOTAL * 100)}, échouées {pct(KO / TOTAL * 100)}" class="en-split">'
      f'<span style="flex: {OK} 1 0; background: {BLUE}"></span><span style="flex: {KO} 1 0; background: {RED}"></span></div>'
      '<div class="en-leg">'
      f'<span><i style="background: {BLUE}"></i>Réussies <strong>{nf(OK)}</strong></span>'
      f'<span><i style="background: {RED}"></i>Échouées <strong>{nf(KO)}</strong></span></div>'
      '</div>\n<div class="en-cards en-c3 en-pre-cards au-p1cards">'
      + scard('user_ok', 'Réussies', nf(OK), f'{pct(OK / TOTAL * 100)} des requêtes')
      + scard('rejet', 'Échouées', nf(KO), f'{pct(KO / TOTAL * 100)} des requêtes')
      + scard('finger', 'Biométriques', nf(TYPES[0][2]), f'{pct(TYPES[0][2] / TOTAL * 100)} des requêtes')
      + scard('otp', 'Code à usage unique', nf(TYPES[1][2]), f'{pct(TYPES[1][2] / TOTAL * 100)} des requêtes')
      + scard('idcard', 'Démographiques et combinées', nf(_demo), f'{pct(_demo / TOTAL * 100)} des requêtes')
      + scard('partner', 'Partenaires raccordés', '1', 'Atos, 100 % des requêtes')
      + '</div>\n</div>\n</section>\n')

# =============== 2. Par type + causes ===============
_trows = []
for label, code, n, f in TYPES:
    r = f / n * 100
    _trows.append([f'<span class="au-tl"><span>{label}</span><span>{code}</span></span>', nf(n), pct(n / TOTAL * 100), nf(f),
                   f'<strong class="{"au-hi" if r >= 50 else ""}">{pct(r)}</strong>'])
TYPES_SEC = ('<section aria-labelledby="types" class="v7-panel">\n' + EN.head('types', 'Par type d’authentification', 'Requêtes et échecs pour chaque type.') +
             '<div class="v7-pbody ab-tpad">\n'
             + V5.table('Authentifications par type', 'au-t5', 270, ['Type', 'Requêtes', 'Part', 'Échecs', 'Taux d’échec'], _trows,
                        ['Total', nf(TOTAL), '100 %', nf(KO), pct(KO / TOTAL * 100)])
             + '</div>\n</section>\n')
_cmax = max(c[1] for c in CAUSES)
CAUSES_SEC = ('<section aria-labelledby="causes" class="v7-panel">\n' + EN.head('causes', 'Causes des échecs', f'{nf(KO)} échecs, du plus fréquent au moins fréquent.') +
              '<div class="v7-pbody ab-cent">\n<div role="table" aria-label="Causes des échecs d’authentification" style="font-variant-numeric: tabular-nums">\n'
              + ''.join(f'<div role="row" class="au-cr"><span role="cell" class="ab-rkn">{i + 1}</span>'
                        f'<span role="rowheader" class="au-cl">{c}</span>'
                        f'<span role="cell" class="au-cn"><strong>{nf(n)}</strong><span>{pct(n / KO * 100)}</span></span>'
                        f'<span role="cell" aria-hidden="true" class="au-cb"><span style="width: {n / _cmax * 100:.1f}%"></span></span></div>\n'
                        for i, (c, n) in enumerate(CAUSES))
              + '</div>\n</div>\n</section>\n')
ROW2 = '<div class="en-row2 au-row2">\n' + TYPES_SEC + CAUSES_SEC + '</div>\n'

# =============== 3. Semaines + partenaire ===============
WEEK_CHART = ('<p aria-live="polite" class="en-read">{{readout}}</p>\n'
              + V5.plot_open(3, 300, V5.yaxis(['15 000', '10 000', '5 000', '0'], 48)) +
              '<sc-for list="{{weeks}}" as="w" hint-placeholder-count="12">\n'
              '<button type="button" onMouseEnter="{{w.enter}}" onFocus="{{w.enter}}" aria-label="{{w.aria}}" class="ab-vb" style="background: {{w.band}}">'
              '<span class="ab-stk" style="width: min(26px, 60%)"><span style="height: {{w.hKo}}px; background: #D03B3B; border-radius: 3px 3px 0 0"></span>'
              '<span style="height: {{w.hOk}}px; background: #2A78D6; border-top: 1px solid #FFFFFF"></span></span></button>\n'
              '</sc-for>\n</div>\n</div>\n'
              + V5.xlabels('weeks', 'w', '{{w.label}}') + '</div>\n</div>\n</div>\n')
WEEKS = ('<section aria-labelledby="semaines" class="v7-panel">\n'
         + EN.head('semaines', 'Requêtes par semaine', '12 dernières semaines complètes.', V5.leg([('Réussies', V5.sq(BLUE)), ('Échouées', V5.sq(RED))])) +
         '<div class="v7-pbody en-hebdo">\n' + WEEK_CHART + '</div>\n</section>\n')
PARTNER = ('<section aria-labelledby="partenaire" class="v7-panel">\n' + EN.head('partenaire', 'Partenaires raccordés', 'Un seul partenaire envoie des requêtes.') +
           '<div class="v7-pbody en-hebdo">\n<div class="au-pf">\n'
           f'<div class="au-ph">{IC["partner"]}<div><p class="au-pn">Atos</p><p class="au-ps">100 % des requêtes</p></div></div>\n'
           f'<div role="img" aria-label="Atos : réussies {pct(OK / TOTAL * 100)}, échouées {pct(KO / TOTAL * 100)}" class="en-split">'
           f'<span style="flex: {OK} 1 0; background: {BLUE}"></span><span style="flex: {KO} 1 0; background: {RED}"></span></div>\n'
           '<dl class="au-kv">'
           f'<div><dt>Requêtes</dt><dd>{nf(TOTAL)}</dd></div>'
           f'<div><dt><i style="background: {BLUE}"></i>Réussies</dt><dd>{nf(OK)}<span>{pct(OK / TOTAL * 100)}</span></dd></div>'
           f'<div><dt><i style="background: {RED}"></i>Échouées</dt><dd>{nf(KO)}<span>{pct(KO / TOTAL * 100)}</span></dd></div>'
           '</dl>\n</div>\n</div>\n</section>\n')
ROW3 = '<div class="en-row2 ab-row3">\n' + WEEKS + PARTNER + '</div>\n'

BODY = TITLE + P1 + ROW2 + ROW3

_W = [['20/10', '20 octobre', 9800, 0.55], ['27/10', '27 octobre', 10400, 0.56], ['03/11', '3 novembre', 11200, 0.57],
      ['10/11', '10 novembre', 11900, 0.58], ['17/11', '17 novembre', 11500, 0.57], ['24/11', '24 novembre', 12300, 0.58],
      ['01/12', '1er décembre', 12800, 0.59], ['08/12', '8 décembre', 12100, 0.58], ['15/12', '15 décembre', 8100, 0.60],
      ['22/12', '22 décembre', 6900, 0.61], ['29/12', '29 décembre', 9200, 0.58], ['05/01', '5 janvier', 9600, 0.59]]
assert "['05/01', '5 janvier', 9600, 0.59]" in OLD.SCRIPT
SCRIPT = f'''class Component extends DCLogic {{
  renderVals() {{
    const st = this.state || {{}};
    const nf = (n) => Math.round(n).toLocaleString('fr-FR').replace(/[  ]/g, ' ');
    const pct = (x) => x.toFixed(1).replace('.', ',') + ' %';
    const W = {json.dumps(_W, ensure_ascii=False)};
    const hov = typeof st.hover === 'number' ? st.hover : W.length - 1;
    const H = 220, MAX = 15000;
    const weeks = W.map((w, i) => {{
      const ko = Math.round(w[2] * w[3]), ok = w[2] - ko;
      return {{ label: i % 2 === 0 ? w[0] : '', hOk: (ok / MAX * H).toFixed(1), hKo: (ko / MAX * H).toFixed(1),
        band: i === hov ? 'rgba(42,120,214,0.07)' : 'transparent',
        aria: 'Semaine du ' + w[1] + ' : ' + nf(w[2]) + ' requêtes, dont ' + nf(ko) + ' échouées',
        enter: () => this.setState({{ hover: i }}) }};
    }});
    const hw = W[hov], hko = Math.round(hw[2] * hw[3]);
    const readout = 'Semaine du ' + hw[1] + ' : ' + nf(hw[2]) + ' requêtes, ' + nf(hw[2] - hko) + ' réussies et ' + nf(hko) + ' échouées.';
    return {{ weeks: weeks, readout: readout }};
  }}
}}'''

CSS_AU = (
    '.au-p1cards{padding-bottom:40px}.au-row2{grid-template-columns:minmax(0,1.2fr) minmax(0,1fr)}'
    '.au-t5{grid-template-columns:minmax(150px,1.6fr) repeat(4,minmax(64px,1fr))}'
    '.au-tl{display:flex;flex-direction:column}.au-tl>span:first-child{font-weight:500;color:#071B35}.au-tl>span:last-child{font-size:12px;color:#4B5A6E}'
    '.au-hi{color:#8A1F1F}'
    '.au-cr{display:grid;grid-template-columns:28px minmax(0,1fr) auto;column-gap:12px;row-gap:6px;align-items:center;padding:12px 0;border-top:1px solid #EEF2F5}'
    '.au-cr:first-child{border-top:0}.au-cl{font-weight:500;color:#071B35}'
    '.au-cn{display:flex;align-items:baseline;gap:8px;justify-content:flex-end;white-space:nowrap}.au-cn strong{font-weight:600;color:#071B35}.au-cn span{font-size:12px;color:#4B5A6E}'
    '.au-cb{grid-column:2/4;height:8px;background:#F1F4F6;border-radius:0 4px 4px 0}.au-cb>span{display:block;height:8px;background:#D03B3B;border-radius:0 4px 4px 0}'
    '.au-pf{display:flex;flex-direction:column;gap:16px;padding:20px 22px;border:1px solid #F5D77E;border-radius:10px;box-shadow:0 2px 6px rgba(7,27,53,.06)}'
    '.au-ph{display:flex;align-items:center;gap:14px}.au-pn{margin:0;font-size:20px;font-weight:600;color:#013781}.au-ps{margin:0;font-size:12.5px;color:#4B5A6E}'
    '.au-kv{margin:0;display:flex;flex-direction:column}.au-kv>div{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:10px 0;border-top:1px solid #EEF2F5}'
    '.au-kv>div:first-child{border-top:0}.au-kv dt{display:inline-flex;align-items:center;gap:8px;font-size:13px;color:#4B5A6E}.au-kv i{width:10px;height:10px;border-radius:2px}'
    '.au-kv dd{margin:0;font-size:16px;font-weight:600;color:#071B35;font-variant-numeric:tabular-nums}.au-kv dd span{margin-left:8px;font-size:12px;font-weight:400;color:#4B5A6E}'
    '@media (max-width:1100px){.au-row2{grid-template-columns:minmax(0,1fr)}}'
    '@media (max-width:600px){.au-t5{grid-template-columns:minmax(88px,1.3fr) repeat(3,minmax(52px,1fr));gap:8px;font-size:13px;padding-left:2px;padding-right:2px}.au-t5>span:nth-child(3){display:none}}'
)


def build():
    html = page('Authentifications', 'Usage.dc.html', OLD.FILTERS, BODY, SCRIPT, 1758, '')
    for blk in (bandeau('Usage.dc.html'), filters(OLD.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + V3.CSS9 + EN.CSS_EN + V5.CSS_AB + CSS_AU + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
