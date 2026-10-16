"""Enrôlement v5 (6 oct. 2026) : refonte au langage de la Vue d'ensemble.

- Titre, pastille de fraîcheur et filtres en pastilles dans le bandeau bleu (plus de bandeau rouge ni de barre de filtres).
- Panneaux blancs à en-tête séparé par un filet (classes v7-* de p_main_v3), chiffres en cellules à filets.
- Devenir des inscriptions aligné sur la Vue d'ensemble : NIU 3 058 886, en cours 123 639 (dont 118 402 bloqués
  depuis plus de 30 jours), échoués 9 218, rejetés 86 496 (somme = 3 278 239 inscriptions).
- Territoire : chiffres de la zone, carte et tableau dans un seul panneau ; les taux régionaux de rejet et d'en cours
  sont recalés pour que leur somme nationale donne 86 496 et 123 639 ; une part fixe d'échoués (9 218) est retirée des NIU.
Le script (carte, semaines, territoire, pyramide, centres) reste celui de p_enrol, nettoyé par clean.py puis ajusté ici.
"""
import re
from common import *
import common_map as CM
import p_enrol, p_main_v3 as V3, clean
import journey_flow as JF

INS, NIU, EC, ECH, REJ, BLOQ = JF.INS, JF.NIU, JF.EC, JF.ECH, JF.REJ, 118402
assert NIU + EC + ECH + REJ == INS and BLOQ < EC
MUTED, INK = '#4B5A6E', '#071B35'


def nf(n):
    return f'{n:,}'.replace(',', ' ')


def pc(x):
    return f'{x:.1f}'.replace('.', ',') + ' %'


# =============== Script : celui de p_enrol, nettoyé, puis ajusté ===============
_old = clean.clean('Enrolement.dc.html', p_enrol.build())
SCRIPT = _old[_old.index('<script type="text/x-dc" data-dc-script'):]
SCRIPT = SCRIPT[SCRIPT.index('>') + 1:SCRIPT.index('</script>')].strip('\n')


def swap(old, new, count=1):
    global SCRIPT
    assert SCRIPT.count(old) == count, (old[:70], SCRIPT.count(old))
    SCRIPT = SCRIPT.replace(old, new)


# 1. devenir des inscriptions : même découpage que la Vue d'ensemble
swap("""      { label: 'NIU générés', n: 3058886, color: '#B4BFCB', note: '' },
      { label: 'En cours', n: 14455, color: '#2A78D6', note: ', depuis 30 jours ou moins' },
      { label: 'Bloqués', n: 118402, color: '#FAB219', note: ', depuis plus de 30 jours' },
      { label: 'Rejetés', n: 86496, color: '#D03B3B', note: '' }""",
     f"""      {{ label: 'NIU générés', n: {NIU}, color: '#013781', note: '' }},
      {{ label: 'En cours', n: {EC}, color: '#FAB219', note: ', dont {nf(BLOQ)} bloqués depuis plus de 30 jours' }},
      {{ label: 'Échoués', n: {ECH}, color: '#EC835A', note: '' }},
      {{ label: 'Rejetés', n: {REJ}, color: '#D03B3B', note: '' }}""")
# 2. territoire : taux régionaux recalés sur les totaux nationaux, échoués retirés des NIU
_R_END = re.search(r"const R = \[.*?\n    \];\n", SCRIPT, re.S)
assert _R_END
_KR, _KC = 'KR', 'KC'
SCRIPT = SCRIPT.replace(_R_END.group(0), _R_END.group(0) + f"""    // recalage : la somme des régions redonne les totaux nationaux ({nf(REJ)} rejetés, {nf(EC)} en cours)
    (() => {{ let n0 = 0, r0 = 0, c0 = 0; R.forEach((r) => r.prefs.forEach((p) => {{ n0 += p[1]; r0 += p[1] * p[2] / 100; c0 += p[1] * p[3] / 100; }}));
      const kr = {REJ} / r0, kc = {EC} / c0; R.forEach((r) => r.prefs.forEach((p) => {{ p[2] = p[2] * kr; p[3] = p[3] * kc; }})); }})();
    const ECHP = {ECH} / NAT * 100;
""", 1)
swap("100 - cur.rej - cur.cours", "100 - cur.rej - cur.cours - ECHP")
swap("100 - s.rej - s.cours", "100 - s.rej - s.cours - ECHP")
swap("nf(cur.n - cur.rejN - cur.coursN) + ' NIU'", "nf(cur.n * (1 - ECHP / 100) - cur.rejN - cur.coursN) + ' NIU'")
swap("{ label: 'En cours', value: nf(132857), detail: '4,1 % des inscriptions' }",
     f"{{ label: 'En cours', value: nf({EC}), detail: '{pc(EC / INS * 100)} des inscriptions' }}")

# =============== Bandeau : titre, fraîcheur, filtres ===============
def pill(label, options, min_w, values=None, attrs=''):
    vals = values or [None] * len(options)
    opts = ''.join(f'<option value="{v}">{o}</option>' if v is not None else f'<option>{o}</option>' for o, v in zip(options, vals))
    return f'<label class="v5-filter"><span>{label}</span><select {attrs}style="min-width: {min_w}px">{opts}</select></label>'


FRESH = ('<a href="Technique.dc.html" class="v5-fresh"><svg width="15" height="15" viewBox="0 0 24 24" aria-hidden="true" '
         'style="fill: none; stroke: #D03B3B; stroke-width: 2.4; stroke-linecap: round"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>'
         'Données au 14/01/2026</a>')
TITLE = ('<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 14px">\n'
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px">'
         '<h1 style="margin: 0; font-size: 30px; font-weight: 600; letter-spacing: -0.015em; color: #FFFFFF">Enrôlement</h1>' + FRESH + '</div>\n'
         '<form aria-label="Filtres appliqués à toute la page" style="display: flex; flex-wrap: wrap; gap: 10px">'
         + pill('Période', ['Depuis le début', '7 derniers jours', '30 derniers jours', '90 derniers jours', 'Période personnalisée'], 150)
         + pill('Région', ['Toutes les régions', 'Grand Lomé', 'Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'], 150,
                values=['', 'DAGL', 'MAR', 'PLA', 'CEN', 'KAR', 'SAV'], attrs='value="{{regionValue}}" onChange="{{onRegion}}" ')
         + pill('Demande', ['Toutes', 'Nouvelle inscription', 'Mise à jour', 'Récupération de NIU'], 110)
         + pill('Genre', ['Tous', 'Femmes', 'Hommes'], 70)
         + pill('Âge', ['Tous les âges', '0 à 5 ans', '6 à 14 ans', '15 à 18 ans', '19 à 25 ans', '26 à 35 ans', '36 à 45 ans', '46 à 60 ans', 'Plus de 60 ans'], 110)
         + '</form>\n</div>\n')


def head(hid, title_, sub='', right=''):
    s = f'<p class="en-sub">{sub}</p>' if sub else ''
    return f'<div class="v7-head"><div><h2 id="{hid}" class="en-h2">{title_}</h2>{s}</div>{right}</div>\n'


# =============== 1. Pré-inscription ===============
_RES, _ATT, _PRE = 546964, 59886, JF.PRE
PREREG = ('<section aria-labelledby="prereg" class="v7-panel">\n' + head('prereg', 'Pré-inscription') +
          '<div class="en-pre">\n<div class="en-pre-main">'
          f'<p class="en-big"><span class="en-bigv">{nf(_PRE)}</span><span class="en-bigu">demandes de pré-enrôlement</span></p>'
          f'<div role="img" aria-label="Rendez-vous réservé {pc(_RES / _PRE * 100)}, en attente de rendez-vous {pc(_ATT / _PRE * 100)}" class="en-split">'
          f'<span style="flex: {_RES} 1 0; background: #013781"></span><span style="flex: {_ATT} 1 0; background: #6DA7EC"></span></div>'
          '<div class="en-leg">'
          f'<span><i style="background: #013781"></i>Rendez-vous réservé <strong>{pc(_RES / _PRE * 100)}</strong></span>'
          f'<span><i style="background: #6DA7EC"></i>En attente de rendez-vous <strong>{pc(_ATT / _PRE * 100)}</strong></span></div>'
          '</div>\n'
          '<dl class="en-facts">\n<sc-for list="{{prereg}}" as="p" hint-placeholder-count="6">\n'
          '<div><dt>{{p.label}}</dt><dd class="en-fv" style="color: {{p.valueColor}}">{{p.value}}</dd><dd class="en-fd">{{p.detail}}</dd></div>\n'
          '</sc-for>\n</dl>\n</div>\n</section>\n')

# =============== 2. Devenir des inscriptions + semaines ===============
DEVENIR = ('<section aria-labelledby="devenir" class="v7-panel en-dev">\n' + BRACKETS + head('devenir', 'Devenir des inscriptions') +
           '<div class="v7-pbody en-devb">'
           f'<p class="en-big"><span class="en-bigv">{nf(NIU)}</span><span class="en-bigu">NIU générés, soit {pc(NIU / INS * 100)} des {nf(INS)} inscriptions</span></p>'
           f'<div role="img" aria-label="Devenir des inscriptions : NIU générés {pc(NIU / INS * 100)}, en cours {pc(EC / INS * 100)}, échoués {pc(ECH / INS * 100)}, rejetés {pc(REJ / INS * 100)}" class="en-split">\n'
           '<sc-for list="{{parts}}" as="p" hint-placeholder-count="4"><span title="{{p.tip}}" style="flex: {{p.w}} 1 0; background: {{p.color}}"></span></sc-for>\n</div>\n'
           '<dl class="en-parts">\n<sc-for list="{{parts}}" as="p" hint-placeholder-count="4">\n'
           '<div><dt><i style="background: {{p.color}}"></i>{{p.label}}</dt><dd class="en-pv">{{p.value}}</dd><dd class="en-pd">{{p.pct}}</dd></div>\n'
           '</sc-for>\n</dl>\n</div>\n</section>\n')

_old_body = _old[_old.index('</helmet>'):]
HEBDO_CHART = re.search(r'(<p aria-live="polite" style="margin: 0; padding: 8px 12px;.*?</div>\n</div>\n</div>\n)</section>', _old_body, re.S).group(1)
HEBDO_CHART = HEBDO_CHART.replace('<p aria-live="polite" style="margin: 0; padding: 8px 12px; border-radius: 6px; background: #F1F4F6; font-size: 13px; color: #071B35">',
                                  '<p aria-live="polite" class="en-read">', 1)
assert 'en-read' in HEBDO_CHART and '{{trend}}' in HEBDO_CHART
_LEG = ('<div class="en-leg" style="margin-top: 0">'
        '<span><i style="background: #2A78D6"></i>Inscriptions</span>'
        '<span><i style="width: 16px; height: 2px; border-radius: 0; background: #1BAF7A"></i>NIU générés</span></div>')
HEBDO = ('<section aria-labelledby="hebdo" class="v7-panel">\n' + head('hebdo', 'Inscriptions et NIU par semaine', '12 dernières semaines complètes.', _LEG) +
         '<div class="v7-pbody en-hebdo">\n' + HEBDO_CHART + '</div>\n</section>\n')
ROW2 = '<div class="en-row2">\n' + DEVENIR + HEBDO + '</div>\n'

# =============== 3. Territoire : chiffres, carte, tableau ===============
_crumb = re.search(r'<nav aria-label="Fil d\'Ariane".*?</nav>', _old_body, re.S).group(0)
_crumb = _crumb.replace('style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: 13px; color: #4B5A6E; min-height: 28px"', 'class="en-crumb"', 1)
assert 'en-crumb' in _crumb
FIGS = ('<dl class="en-figs" aria-label="Chiffres de la zone">\n<sc-for list="{{figures}}" as="k" hint-placeholder-count="5">\n'
        '<div><dt>{{k.label}}</dt><dd class="en-kv">{{k.value}}</dd><dd class="en-kd">{{k.detail}}</dd></div>\n</sc-for>\n</dl>\n')
MAPBLOCK = CM.block('map', 440, CM.legend('Taux de rejet', ['&lt; 2,5 %', '2,5 à 3 %', '3 à 3,5 %', '3,5 % et +']), brackets=False)
_CHEV = '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="fill: none; stroke: currentColor; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round"><polyline points="9 6 15 12 9 18"></polyline></svg>'
TABLE = ('<div class="v7-reg-tab">\n<p class="en-tt" id="souszones">{{tableTitle}}</p>\n'
         '<div role="table" aria-labelledby="souszones" class="en-table">\n'
         '<div role="row" class="en-tr en-th"><span role="columnheader">Zone</span><span role="columnheader">Inscriptions</span>'
         '<span role="columnheader">NIU générés</span><span role="columnheader">Rejets</span><span role="columnheader">En cours</span><span role="columnheader">Délai médian</span></div>\n'
         '<sc-for list="{{rows}}" as="r" hint-placeholder-count="6">\n<div role="row" class="en-tr">\n<span role="rowheader">'
         '<sc-if value="{{r.canDrill}}" hint-placeholder-val="{{true}}"><button type="button" onClick="{{r.drill}}" class="en-drill">{{r.name}}' + _CHEV + '</button></sc-if>'
         '<sc-if value="{{r.cannotDrill}}" hint-placeholder-val="{{false}}"><span class="en-zn">{{r.name}}</span></sc-if></span>\n'
         '<span role="cell" title="{{r.tip}}">{{r.value}}</span><span role="cell">{{r.niu}}</span>'
         '<span role="cell" style="font-weight: {{r.rejWeight}}"><sc-if value="{{r.high}}" hint-placeholder-val="{{false}}">'
         '<svg width="11" height="11" viewBox="0 0 24 24" aria-label="Taux élevé" style="margin-right: 4px; fill: #FAB219"><path d="M12 2 1 21h22L12 2z"></path></svg></sc-if>{{r.rej}}</span>'
         '<span role="cell">{{r.cours}}</span><span role="cell">{{r.delai}}</span>\n</div>\n</sc-for>\n</div>\n</div>\n')
TERR = ('<section aria-labelledby="terr" class="v7-panel">\n'
        '<div class="v7-head"><div>' + _crumb + '<h2 id="terr" class="en-h2">{{zoneTitle}}</h2>'
        '<p class="en-sub">Carte colorée selon le taux de rejet. Cliquez sur une région pour voir ses préfectures.</p></div></div>\n'
        + FIGS + '<div class="v7-pbody v7-reg">\n<div class="v7-reg-map">\n' + MAPBLOCK + '</div>\n' + TABLE + '</div>\n</section>\n')

# =============== 4. Âge et sexe, centres ===============
_pyr = re.search(r'(<div style="display: grid; grid-template-columns: minmax\(0, 1fr\) 72px minmax\(0, 1fr\); gap: 8px; font-size: 13px">.*?</sc-for>\n</div>\n)</section>', _old_body, re.S).group(1)
PYRAMIDE = ('<section aria-labelledby="pyramide" class="v7-panel">\n' + head('pyramide', 'NIU générés par âge et par sexe', '{{zoneLabel}}, en pourcentage des NIU de la zone') +
            '<div class="v7-pbody en-pyr">\n' + _pyr + '</div>\n</section>\n')
_csc = re.search(r'<section aria-labelledby="csc".*?</section>', _old_body, re.S).group(0)
_tabs = re.search(r'<div role="group" aria-label="Classement affiché".*?</div>', _csc, re.S).group(0)
_inner = _csc[_csc.index('<sc-if value="{{hasCsc}}"'):_csc.rindex('</section>')]
CENTRES = ('<section aria-labelledby="csc" class="v7-panel">\n' + head('csc', 'Centres de la zone', '{{zoneLabel}}', _tabs) +
           '<div class="v7-pbody en-csc">\n' + _inner + '</div>\n</section>\n')
ROW4 = '<div class="en-row2 en-row4">\n' + PYRAMIDE + CENTRES + '</div>\n'

BODY = TITLE + PREREG + ROW2 + TERR + ROW4
for h in ('{{prereg}}', '{{parts}}', '{{trend}}', '{{figures}}', '{{rows}}', '{{pyramid}}', '{{cscRows}}', '{{map.items}}', '{{zoneTitle}}', '{{goNational}}'):
    assert h in BODY, h

CSS_EN = (
    '.en-h2{margin:0;font-size:20px;font-weight:600;color:#071B35}.en-sub{margin:4px 0 0;font-size:13px;color:#4B5A6E}'
    '.en-big{margin:0;display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 12px}'
    '.en-bigv{font-size:38px;font-weight:600;letter-spacing:-0.025em;line-height:1.1;color:#071B35;font-variant-numeric:tabular-nums}'
    '.en-bigu{font-size:14px;color:#4B5A6E}'
    '.en-split{display:flex;gap:2px;height:10px;border-radius:5px;overflow:hidden}.en-split>span{min-width:3px}'
    '.en-leg{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:12.5px;color:#4B5A6E}'
    '.en-leg>span{display:inline-flex;align-items:center;gap:7px}.en-leg i{width:10px;height:10px;border-radius:2px}.en-leg strong{font-weight:600;color:#071B35}'
    '.en-pre{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.6fr);border-radius:0 0 14px 14px;overflow:hidden}'
    '.en-pre-main{padding:24px 28px 28px;display:flex;flex-direction:column;gap:14px;border-right:1px solid #E6EBF0}'
    '.en-facts{margin:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:#E6EBF0}'
    '.en-facts>div{background:#FFFFFF;padding:20px 24px;display:flex;flex-direction:column;gap:3px;min-width:0}'
    '.en-facts dt{font-size:12.5px;color:#4B5A6E}.en-fv{margin:0;font-size:22px;font-weight:600;letter-spacing:-0.01em;font-variant-numeric:tabular-nums}'
    '.en-fd{margin:0;font-size:12px;line-height:1.4;color:#4B5A6E}'
    '.en-row2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:24px;align-items:stretch}'
    '.en-row4{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}'
    '.en-dev{position:relative}.en-devb{display:flex;flex-direction:column;gap:18px}'
    '.en-parts{margin:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:#E6EBF0;border-top:1px solid #E6EBF0}'
    '.en-parts>div{background:#FFFFFF;padding:14px 4px 4px 0;display:flex;flex-direction:column;gap:1px;min-width:0}'
    '.en-parts dt{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;color:#4B5A6E}.en-parts i{width:10px;height:10px;border-radius:2px}'
    '.en-pv{margin:0;font-size:20px;font-weight:600;color:#071B35;font-variant-numeric:tabular-nums}.en-pd{margin:0;font-size:12px;line-height:1.4;color:#4B5A6E}'
    '.en-hebdo{display:flex;flex-direction:column;gap:12px}'
    '.en-read{margin:0;font-size:13px;color:#071B35;padding-left:10px;border-left:3px solid #2A78D6}'
    '.en-crumb{display:flex;flex-wrap:wrap;align-items:center;gap:6px;min-height:24px;margin-bottom:2px;font-size:12.5px;color:#4B5A6E}'
    '.en-figs{margin:0;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:1px;background:#E6EBF0;border-bottom:1px solid #E6EBF0}'
    '.en-figs>div{background:#FFFFFF;padding:18px 24px;display:flex;flex-direction:column;gap:2px;min-width:0}'
    '.en-figs dt{font-size:12.5px;color:#4B5A6E}.en-kv{margin:0;font-size:24px;font-weight:600;letter-spacing:-0.015em;color:#071B35;font-variant-numeric:tabular-nums;white-space:nowrap}'
    '.en-kd{margin:0;font-size:12px;color:#4B5A6E}'
    '.en-tt{margin:0 0 6px;font-size:15px;font-weight:600;color:#071B35}'
    '.en-table{min-width:440px;font-variant-numeric:tabular-nums}'
    '.en-tr{display:grid;grid-template-columns:minmax(104px,1.3fr) repeat(5,minmax(62px,1fr));gap:12px;align-items:center;padding:0 8px;border-top:1px solid #EEF2F5}'
    '.en-tr>span:not(:first-child){text-align:right}'
    '.en-th{align-items:end;padding-top:6px;padding-bottom:8px;border-top:0;font-size:12px;line-height:1.35;color:#4B5A6E}'
    '.en-drill{display:inline-flex;align-items:center;gap:4px;min-height:42px;padding:0;border:0;background:transparent;font-family:inherit;font-size:14px;font-weight:600;color:#013781;cursor:pointer;text-align:left}'
    '.en-drill:hover{color:#071B35}.en-zn{display:inline-flex;align-items:center;min-height:42px;font-weight:500}'
    '.en-pyr{display:flex;flex-direction:column;gap:14px}.en-csc{display:flex;flex-direction:column;gap:6px;padding-top:12px}'
    '@media (max-width:1240px){.en-tr{gap:8px;padding:0 4px;font-size:13.5px}.en-th{font-size:11.5px}.en-figs>div{padding:16px 18px}.en-kv{font-size:21px}}'
    '@media (max-width:1100px){.en-pre,.en-row2{grid-template-columns:minmax(0,1fr)}.en-pre-main{border-right:0;border-bottom:1px solid #E6EBF0}'
    '}'
    '@media (max-width:1000px){.en-tr{gap:12px;font-size:inherit}}'
    '@media (max-width:860px){.en-figs{grid-template-columns:repeat(2,minmax(0,1fr))}.en-figs>div:last-child:nth-child(odd){grid-column:1/-1}}'
    '@media (max-width:700px){.en-facts{grid-template-columns:repeat(2,minmax(0,1fr))}'
    '.en-pre-main,.en-facts>div,.en-figs>div{padding:16px 20px}.en-parts{grid-template-columns:minmax(0,1fr)}.en-bigv{font-size:32px}}'
)


def build():
    html = page('Enrôlement', 'Enrolement.dc.html', p_enrol.FILTERS, BODY, SCRIPT, 2600, '')
    for blk in (bandeau('Enrolement.dc.html'), filters(p_enrol.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + CSS_EN + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
