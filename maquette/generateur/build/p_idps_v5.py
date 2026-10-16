"""IDPS v5 (8 oct. 2026) : refonte au langage de la Vue d'ensemble, de l'Enrôlement, de l'Impression des cartes et de l'ABIS.

Chiffres réels du BI actuel (inchangés) : 14 ordres reçus depuis MOSIP, 14 en attente, 0 carte imprimée,
14 erreurs (personnalisation 3, contrôle qualité 5, supervision 6), tous en Savanes, tous la semaine du 29 juin 2026.
- Bandeau : titre « IDPS », pastille jaune « Dernière mise à jour : 03/07/2026 à 17h09 » à droite, filtres en pastilles.
- Ordres d'impression (crochets jaunes) : chiffre principal, barre en attente / imprimées et 6 cartes v9.
- Où les ordres échouent (étapes de production) et erreurs par type côte à côte.
- Ordres et erreurs par région et par semaine côte à côte (graphique au survol, comme les autres pages).
"""
import datetime
import json
from common import *
import p_idps as OLD, p_main_v3 as V3, p_enrol_v5 as EN, p_bio_v5 as V5, p_cartes_v5 as CA

IC = dict(V5.IC)
IC.update({k: CA.IC[k] for k in ('doc', 'print', 'idcard')})
RED, NAVY, BLUE = '#D03B3B', '#013781', '#2A78D6'


def scard(icon, label, value, detail):
    return (f'<div class="v9-card en-card">{IC[icon]}<span class="v9-body"><span class="v9-name">{label}</span>'
            f'<span class="v9-val">{value}</span><span class="v9-sub">{detail}</span></span></div>')


REC, ATT, IMP, ERR = 14, 14, 0, 14
STAGES = OLD.STAGES                      # (étape, ordres entrés, erreurs)
assert sum(e for _, _, e in STAGES) == ERR
TYPES = [('Supervision', 6, '03/07/2026 à 16h48'), ('Contrôle qualité', 5, '03/07/2026 à 17h09'), ('Personnalisation', 3, '03/07/2026 à 17h01')]
assert sum(n for _, n, _ in TYPES) == ERR

# =============== Bandeau ===============
TITLE = ('<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 14px">\n'
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px; align-self: stretch">'
         '<h1 style="margin: 0; font-size: 30px; font-weight: 600; letter-spacing: -0.015em; color: #FFFFFF">IDPS</h1>'
         + EN.FRESH.replace('14/01/2026 à 11h42', '03/07/2026 à 17h09') + '</div>\n'
         '<form aria-label="Filtres appliqués à toute la page" style="display: flex; flex-wrap: wrap; gap: 10px">'
         + EN.pill('Période', ['Depuis le début', '7 derniers jours', '30 derniers jours', '90 derniers jours', 'Période personnalisée'], 150)
         + EN.pill('Région', ['Toutes les régions', 'Grand Lomé', 'Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'], 150)
         + EN.pill('Type d’erreur', ['Tous les types', 'Personnalisation', 'Contrôle qualité', 'Supervision'], 130)
         + '</form>\n</div>\n')
assert '03/07/2026 à 17h09' in TITLE

# =============== 1. Ordres d'impression ===============
P1 = ('<section aria-labelledby="ordres" class="v7-panel en-dev">\n' + BRACKETS + EN.head('ordres', 'Ordres d’impression', 'Nouveau circuit d’impression IDPS, en pilote : il ne compte pas les 3 101 590 cartes de la page Impression des cartes.') +
      '<div class="en-pre">\n<div class="en-pre-main">'
      f'<p class="en-big"><span class="en-bigv">{REC}</span><span class="en-bigu">ordres d’impression reçus depuis MOSIP, tous le 03/07/2026</span></p>'
      f'<div role="img" aria-label="Ordres reçus : {ATT} en attente, {IMP} imprimé" class="en-split">'
      f'<span style="flex: {ATT} 1 0; background: #FAB219"></span></div>'
      '<div class="en-leg">'
      f'<span><i style="background: #FAB219"></i>En attente <strong>{ATT}</strong></span>'
      f'<span><i style="background: {NAVY}"></i>Imprimés <strong>{IMP}</strong></span></div>'
      '<p class="ab-note">Les 14 ordres sont à la fois en attente et en erreur.</p>'
      '</div>\n<div class="en-cards en-c3 en-pre-cards id-p1cards">'
      + scard('wait', 'En attente', str(ATT), f'Les {REC} ordres reçus')
      + scard('idcard', 'Cartes imprimées', str(IMP), 'Aucune depuis le début')
      + scard('echec', 'Erreurs', str(ERR), 'Une par ordre reçu')
      + '</div>\n</div>\n</section>\n')

# =============== 2. Où les ordres échouent + erreurs par type ===============
_rows = ''
for name, n_in, n_err in STAGES:
    ok = n_in - n_err
    _rows += (f'<div role="row" class="id-st"><span role="rowheader" class="id-stn">{name}</span><span role="cell" class="id-stv">{n_in}</span>'
              f'<span role="cell" class="id-stb" aria-label="{ok} ordres passent, {n_err} erreurs">'
              + (f'<span title="{name} : {ok} ordres passent" style="flex: {ok} 1 0; background: {NAVY}"></span>' if ok else '')
              + f'<span title="{name} : {n_err} erreurs" style="flex: {n_err} 1 0; background: {RED}"></span>'
              + f'<span style="flex: {REC - n_in} 1 0; background: transparent"></span></span>'
              f'<span role="cell" class="id-ste">{n_err}</span></div>\n')
_rows += ('<div role="row" class="id-st id-stt"><span role="rowheader" class="id-stn">Cartes imprimées</span><span role="cell" class="id-stv">0</span>'
          '<span role="cell" class="id-stb"><span style="flex: 1 1 0; background: #F1F4F6"></span></span><span role="cell"></span></div>\n')
FAIL = ('<section aria-labelledby="echecs" class="v7-panel">\n'
        + EN.head('echecs', 'Où les ordres échouent', 'Étapes de production d’une carte, dans l’ordre, sur les 14 ordres reçus.',
                  V5.leg([('Ordres qui passent', V5.sq(NAVY)), ('Erreurs', V5.sq(RED))])) +
        '<div class="v7-pbody">\n<div role="table" aria-label="Ordres par étape de production" class="id-sts">\n'
        '<div role="row" class="id-st id-sth"><span role="columnheader">Étape</span><span role="columnheader">Ordres entrés</span>'
        '<span role="columnheader">Sur les 14 ordres reçus</span><span role="columnheader">Erreurs</span></div>\n'
        + _rows + '</div>\n</div>\n</section>\n')

_tmax = max(n for _, n, _ in TYPES)
TYPES_SEC = ('<section aria-labelledby="types" class="v7-panel">\n'
             + EN.head('types', 'Erreurs par type', f'{ERR} erreurs au total, toutes le 3 juillet 2026.') +
             '<div class="v7-pbody ab-cent">\n<div role="table" aria-label="Erreurs d’impression par type" style="font-variant-numeric: tabular-nums">\n'
             + ''.join(f'<div role="row" class="id-tp"><span role="cell" class="ab-rkn">{i + 1}</span>'
                       f'<span role="rowheader" class="ab-rkc"><span>{t}</span><span>Dernière le {last}</span></span>'
                       f'<span role="cell" aria-hidden="true" class="id-tpb"><span style="width: {n / _tmax * 100:.1f}%"></span></span>'
                       f'<span role="cell" class="id-tpn">{n}</span></div>\n' for i, (t, n, last) in enumerate(TYPES))
             + '</div>\n</div>\n</section>\n')
ROW2 = '<div class="en-row2 id-row2">\n' + FAIL + TYPES_SEC + '</div>\n'

# =============== 3. Régions + semaines ===============
_regs = OLD.REGIONS
REG = ('<section aria-labelledby="regions-idps" class="v7-panel">\n' + EN.head('regions-idps', 'Ordres et erreurs par région', 'Régions du nord au sud.') +
       '<div class="v7-pbody ab-tpad">\n'
       + V5.table('Ordres IDPS par région', 'id-t5', 250, ['Région', 'Reçus', 'En attente', 'Imprimés', 'Erreurs'],
                  [[(f'<strong>{n}</strong>' if r else f'<span class="id-mut">{n}</span>')]
                   + [(f'<strong class="id-red">{v}</strong>' if (j == 3 and v) else (str(v) if r else f'<span class="id-mut">{v}</span>')) for j, v in enumerate((r, a, i_, e))]
                   for n, r, a, i_, e in _regs],
                  ['Togo', str(REC), str(ATT), str(IMP), str(ERR)])
       + '</div>\n</section>\n')

# semaines 2026 (semaines ISO 1 à 39) : une seule semaine active, la 27e (29 juin au 5 juillet)
_MO = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
_ML = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
_wk, _prev = [], None
for w in range(1, 28):
    d = datetime.date.fromisocalendar(2026, w, 1)
    e = d + datetime.timedelta(days=6)
    th = d + datetime.timedelta(days=3)
    lab = _MO[th.month - 1] if th.month != _prev else ''
    lcls = 'id-ml id-mo' if lab and th.month % 2 == 0 else 'id-ml'
    _prev = th.month
    rec, err = (14, 14) if w == 27 else (0, 0)
    span = (f'{d.day if d.day > 1 else "1er"} {_ML[d.month - 1]}' + (f' {d.year}' if d.year != e.year else '')
            + f' au {e.day if e.day > 1 else "1er"} {_ML[e.month - 1]}')
    _wk.append([w, lab, rec, err, span, lcls])
WEEK_CHART = ('<p aria-live="polite" class="en-read">{{wkRead}}</p>\n'
              + V5.plot_open(3, 300, V5.yaxis(['15', '10', '5', '0'], 22)) +
              '<sc-for list="{{weeks}}" as="w" hint-placeholder-count="27">\n'
              '<button type="button" onMouseEnter="{{w.enter}}" onFocus="{{w.enter}}" aria-label="{{w.aria}}" class="ab-vb id-wb" style="background: {{w.band}}">'
              '<span style="height: {{w.hR}}px; background: #2A78D6"></span><span style="height: {{w.hE}}px; background: #D03B3B"></span></button>\n'
              '</sc-for>\n</div>\n</div>\n'
              + '<div aria-hidden="true" style="display: flex; margin-top: 6px; font-size: 12px; line-height: 1.3; color: #4B5A6E">\n'
              '<sc-for list="{{weeks}}" as="w" hint-placeholder-count="27"><span class="{{w.lc}}">{{w.label}}</span></sc-for>\n</div>\n'
              + '</div>\n</div>\n</div>\n')
WEEKS = ('<section aria-labelledby="semaines-idps" class="v7-panel">\n'
         + EN.head('semaines-idps', 'Ordres et erreurs par semaine, 2026', 'Une seule semaine active : celle du 29 juin au 5 juillet.',
                   V5.leg([('Ordres reçus', V5.sq(BLUE)), ('Erreurs', V5.sq(RED))])) +
         '<div class="v7-pbody en-hebdo">\n' + WEEK_CHART + '</div>\n</section>\n')
ROW3 = '<div class="en-row2 id-row3">\n' + REG + WEEKS + '</div>\n'

BODY = TITLE + P1 + ROW2 + ROW3
SCRIPT = f'''class Component extends DCLogic {{
  renderVals() {{
    const st = this.state || {{}};
    const wk = {json.dumps(_wk, ensure_ascii=False)};
    const hov = typeof st.hoverW === 'number' ? st.hoverW : 26;
    const H = 220, M = 15;
    const weeks = wk.map((w, i) => ({{ label: w[1], lc: w[5], hR: (w[2] / M * H).toFixed(1), hE: (w[3] / M * H).toFixed(1),
      band: i === hov ? 'rgba(42,120,214,0.08)' : 'transparent',
      aria: 'Semaine ' + w[0] + ', du ' + w[4] + ' : ' + (w[2] ? w[2] + ' ordres reçus, ' + w[3] + ' erreurs' : 'aucun ordre'),
      enter: () => this.setState({{ hoverW: i }}) }}));
    const h = wk[hov];
    const wkRead = 'Semaine ' + h[0] + ', du ' + h[4] + ' : ' + (h[2] ? h[2] + ' ordres reçus, ' + h[3] + ' erreurs.' : 'aucun ordre reçu.');
    return {{ weeks: weeks, wkRead: wkRead }};
  }}
}}'''

CSS_ID = (
    '.id-p1cards{padding-bottom:40px}'
    '.id-row2{grid-template-columns:minmax(0,1.45fr) minmax(0,1fr)}.id-row3{grid-template-columns:minmax(0,1fr) minmax(0,1.5fr)}'
    '.id-sts{font-variant-numeric:tabular-nums}'
    '.id-st{display:grid;grid-template-columns:150px 92px minmax(0,1fr) 64px;gap:14px;align-items:center;padding:13px 0;border-top:1px solid #EEF2F5}'
    '.id-sth{padding:4px 0 8px;border-top:0;font-size:12px;color:#4B5A6E}.id-sth>span:nth-child(2),.id-sth>span:last-child{text-align:right}'
    '.id-stn{font-weight:600;color:#071B35}.id-stv{text-align:right}.id-ste{text-align:right;font-weight:600;color:#8A1F1F}'
    '.id-stb{display:flex;gap:2px;height:14px}.id-stb>span{display:block;min-width:0}.id-stb>span:first-child{border-radius:0}'
    '.id-stt{border-top:1px solid #C5CFDA}.id-stt .id-stv{font-weight:600}'
    '.id-tp{display:grid;grid-template-columns:28px minmax(0,1.2fr) minmax(0,1fr) 36px;gap:12px;align-items:center;padding:12px 0;border-top:1px solid #EEF2F5}'
    '.id-tp:first-child{border-top:0}.id-tpb{height:12px;background:#F1F4F6;border-radius:0 4px 4px 0}'
    '.id-tpb>span{display:block;height:12px;background:#D03B3B;border-radius:0 4px 4px 0}.id-tpn{text-align:right;font-weight:600;color:#071B35}'
    '.id-t5{grid-template-columns:minmax(100px,1.3fr) repeat(4,minmax(56px,1fr))}.id-mut{color:#4B5A6E}.id-red{color:#8A1F1F}'
    '.id-ml{flex:1 1 0;min-width:0;white-space:nowrap;overflow:visible}.id-wb{gap:1px}.id-wb>span{display:block;width:min(6px,40%);border-radius:2px 2px 0 0}'
    '@media (max-width:1100px){.id-row2,.id-row3{grid-template-columns:minmax(0,1fr)}}'
    '@media (max-width:600px){.id-st{grid-template-columns:minmax(0,1fr) 44px 44px;row-gap:6px}.id-st>.id-stb{grid-column:1/-1;grid-row:2}'
    '.id-mo{visibility:hidden}.id-t5{grid-template-columns:minmax(62px,1.1fr) repeat(4,minmax(38px,1fr));gap:6px;font-size:12.5px;padding-left:2px;padding-right:2px}.id-sth>span:nth-child(3){display:none}.id-tp{grid-template-columns:24px minmax(0,1fr) 30px}.id-tpb{display:none}}'
)


def build():
    html = page('IDPS', 'Idps.dc.html', OLD.FILTERS, BODY, SCRIPT, 1712, '')
    for blk in (bandeau('Idps.dc.html'), filters(OLD.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + V3.CSS9 + EN.CSS_EN + V5.CSS_AB + CSS_ID + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
