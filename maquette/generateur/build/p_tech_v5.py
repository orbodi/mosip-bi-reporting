"""Qualité et technique v5 (8 oct. 2026) : refonte au langage des autres pages.

Chiffres inchangés (p_tech, nettoyé par clean.py) : fraîcheur source par source, 7 contrôles de cohérence,
paquets bloqués par étape, statut des paquets, motifs de rejet, types de demande.
- Bandeau : titre, pastille jaune « Dernière mise à jour : 14/01/2026 à 11h59 » à droite, filtres en pastilles.
- État des données (crochets jaunes) : 261 jours sans nouvelles données, barre des contrôles et 6 cartes v9.
- Fraîcheur et contrôles côte à côte ; carte de chaleur pleine largeur ; statut et règle côte à côte ;
  motifs et détail côte à côte ; types de demande.
Les blocs repris du gabarit gardent leur contenu et leur script ; seuls leur cadre et leur en-tête changent.
"""
import re
from common import *
import p_tech as OLD, p_main_v3 as V3, p_enrol_v5 as EN, p_bio_v5 as V5, clean

IC = V5.IC
RED, YEL, GRN = '#D03B3B', '#FAB219', '#1BAF7A'

_old = clean.clean('Technique.dc.html', OLD.build())
SCRIPT = _old[_old.index('<script type="text/x-dc" data-dc-script'):]
SCRIPT = SCRIPT[SCRIPT.index('>') + 1:SCRIPT.index('</script>')].strip('\n')
_body = _old[_old.index('</helmet>'):]


def section(sid):
    m = re.search(r'<section aria-labelledby="%s".*?</section>' % sid, _body, re.S)
    assert m, sid
    return m.group(0)


def inner(sec):
    """Contenu d'une section du gabarit, sans la balise section ni l'en-tête <div><h2>…</h2><p>…</p></div>."""
    s = sec[sec.index('>') + 1:sec.rindex('</section>')]
    m = re.search(r'<div>\n<h2 id="[^"]+"[^>]*>.*?</h2>\n(?:<p[^>]*>.*?</p>\n)?</div>\n', s, re.S)
    assert m, sec[:80]
    return s[m.end():]


def scard(icon, label, value, detail):
    return (f'<div class="v9-card en-card">{IC[icon]}<span class="v9-body"><span class="v9-name">{label}</span>'
            f'<span class="v9-val">{value}</span><span class="v9-sub">{detail}</span></span></div>')


# =============== Bandeau ===============
TITLE = ('<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 14px">\n'
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px; align-self: stretch">'
         '<h1 style="margin: 0; font-size: 30px; font-weight: 600; letter-spacing: -0.015em; color: #FFFFFF">Qualité et technique</h1>'
         + EN.FRESH.replace('14/01/2026 à 11h42', '14/01/2026 à 11h59') + '</div>\n'
         '<form aria-label="Filtres appliqués à toute la page" style="display: flex; flex-wrap: wrap; gap: 10px">'
         + EN.pill('Période', ['Depuis le début', '7 derniers jours', '30 derniers jours', '90 derniers jours', 'Période personnalisée'], 150)
         + EN.pill('Région', ['Toutes les régions', 'Grand Lomé', 'Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'], 150)
         + EN.pill('Type de demande', ['Toutes', 'Nouvelle inscription', 'Mise à jour', 'Récupération de NIU'], 110)
         + '</form>\n</div>\n')
assert '14/01/2026 à 11h59' in TITLE

# =============== 1. État des données ===============
CTRL = [('Non conformes', 3, RED), ('À vérifier', 2, YEL), ('Conformes', 2, GRN)]
P1 = ('<section aria-labelledby="etat" class="v7-panel en-dev">\n' + BRACKETS + EN.head('etat', 'État des données') +
      '<div class="en-pre">\n<div class="en-pre-main">'
      '<p class="en-big"><span class="en-bigv">261 jours</span><span class="en-bigu">sans nouvelles données dans 7 des 8 sources (IDPS : 91 jours)</span></p>'
      '<div role="img" aria-label="Contrôles de cohérence : ' + ', '.join(f'{l} {n}' for l, n, _ in CTRL) + '" class="en-split">'
      + ''.join(f'<span style="flex: {n} 1 0; background: {c}"></span>' for _, n, c in CTRL) + '</div>'
      '<div class="en-leg">' + ''.join(f'<span><i style="background: {c}"></i>{l} <strong>{n}</strong></span>' for l, n, c in CTRL) + '</div>'
      '<p class="ab-note">7 contrôles de cohérence vérifiés à chaque rafraîchissement du BI.</p>'
      '</div>\n<div class="en-cards en-c3 en-pre-cards tq-p1cards">'
      + scard('clock', 'Dernière donnée', '14/01/2026', 'À 11h59 ; IDPS le 03/07/2026')
      + scard('cours', 'Rafraîchissement du BI', '02/10/2026', 'À 09h00, chaque jour')
      + scard('rejet', 'Contrôles non conformes', '3', 'Sur 7 contrôles')
      + scard('echec', 'Contrôles à vérifier', '2', 'Sur 7 contrôles')
      + scard('wait', 'Paquets non terminés', '132 857', 'Dont 38 650 depuis plus de 90 jours')
      + scard('cal_x', 'Paquets bloqués', '118 402', '3,6 % des 3 278 239 paquets')
      + '</div>\n</div>\n</section>\n')

# =============== 2. Fraîcheur + contrôles ===============
FRESH_ROWS = [('Enrôlement', '14/01/2026 à 11h42', '30/09/2026 à 23h00', '261 jours'),
              ('Impression des cartes', '14/01/2026 à 11h59<br><span class="tq-mut">un rejet le 13/03/2026</span>', '01/10/2026 à 09h00', '261 jours'),
              ('Authentification', '14/01/2026 à 11h05', '01/10/2026 à 09h00', '261 jours'),
              ('Pré-inscription', '14/01/2026 à 11h28', '01/10/2026 à 09h00', '261 jours'),
              ('Scores biométriques', '14/01/2026 à 11h37', '02/10/2026 à 08h00', '261 jours'),
              ('IDPS', '03/07/2026 à 17h09', '02/10/2026 à 09h00', '91 jours'),
              ('Transactions ABIS', '14/01/2026 à 11h40', '02/10/2026 à 08h00', '261 jours'),
              ('Adjudication', '14/01/2026 à 10h52', '02/10/2026 à 08h00', '261 jours')]
for _src, _last, _ref, _gap in FRESH_ROWS:
    assert _ref in _body and _last.split('<br>')[0] in _body, _src
FRAICHEUR = ('<section aria-labelledby="fraicheur" class="v7-panel">\n'
             + EN.head('fraicheur', 'Fraîcheur des données, source par source', 'Le BI se rafraîchit chaque jour, mais aucune source ne reçoit de nouvelles données.') +
             '<div class="v7-pbody ab-tpad">\n'
             + V5.table('Fraîcheur des données par source', 'tq-t4', 270, ['Source', 'Dernier événement reçu', 'Rafraîchissement du BI', 'Sans données'],
                        [[s, l, r, f'<strong class="tq-red">{g}</strong>'] for s, l, r, g in FRESH_ROWS])
             + '</div>\n</section>\n')

CHECKS = [('ko', 'Les dossiers « synchronisés mais non reçus » sont positifs ou nuls', 'Valeur actuelle : −16 734'),
          ('ko', 'Le compteur des pré-inscriptions réservées correspond au graphique', '0 sur le compteur, environ 546 964 sur le graphique'),
          ('ko', 'Un ordre d’impression IDPS en erreur ne reste pas « en attente »', '14 ordres à la fois en attente et en erreur'),
          ('warn', 'Les cartes imprimées ne dépassent pas les NIU générés et les réimpressions', 'Écart de +42 704 cartes'),
          ('warn', 'Les cartes expédiées par centre ne dépassent pas ses inscriptions', 'Dépassé pour 4 des 5 centres les plus actifs'),
          ('ok', 'Les rejets pour doublon correspondent aux doublons confirmés en adjudication', '16 002 rejets pour doublon, 16 002 HIT'),
          ('ok', 'Réussies et échouées font le total des authentifications', '215 736 + 294 763 = 510 499')]
_LAB = {'ko': 'Non conforme', 'warn': 'À vérifier', 'ok': 'Conforme'}
for _k, _r, _v in CHECKS:
    assert _r.replace('’', '’') in _body, _r
CONTROLES = ('<section aria-labelledby="controles" class="v7-panel">\n'
             + EN.head('controles', 'Contrôles de cohérence', 'Du plus grave au conforme.') +
             '<div class="v7-pbody ab-cent">\n<ul class="tq-cl">\n'
             + ''.join(f'<li class="tq-c"><span class="tq-st tq-{k}">{_LAB[k]}</span><span class="tq-cr">{r}</span><span class="tq-cv">{v}</span></li>\n'
                       for k, r, v in CHECKS)
             + '</ul>\n</div>\n</section>\n')
ROW2 = '<div class="en-row2 tq-row2">\n' + FRAICHEUR + CONTROLES + '</div>\n'

# =============== 3. Carte de chaleur des blocages ===============
_et = section('etapes')
_lead = re.search(r'<p style="margin: 6px 0 0; font-size: 15px; color: #071B35">(.*?)</p>', _et, re.S).group(1)
_sub = re.search(r'<p style="margin: 4px 0 0; font-size: 13px; color: #4B5A6E">(.*?)</p>', _et, re.S).group(1)
_leg = re.search(r'(<div style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: #4B5A6E">\n<span>Nombre de paquets</span>.*?</div>\n</div>\n)</div>\n', _et, re.S).group(1)
_tab = _et[_et.index('<div style="overflow-x: auto">'):_et.rindex('</section>')]
ETAPES = ('<section aria-labelledby="etapes" class="v7-panel">\n' + EN.head('etapes', 'Où les paquets restent bloqués', _sub, _leg) +
          '<div class="v7-pbody en-hebdo">\n' f'<p class="en-read">{_lead}</p>\n' + _tab + '</div>\n</section>\n')

# =============== 4. Statut + règle ; motifs + détail ===============
STATUTS = ('<section aria-labelledby="statuts" class="v7-panel">\n' + EN.head('statuts', 'Statut des 3 278 239 paquets', 'Quatre statuts lisibles, regroupant les statuts MOSIP.') +
           '<div class="v7-pbody tq-col">\n' + inner(section('statuts')) + '</div>\n</section>\n')
REGLE = ('<section aria-labelledby="correspondance" class="v7-panel">\n' + EN.head('correspondance', 'Règle de regroupement') +
         '<div class="v7-pbody tq-col ab-cent">\n' + inner(section('correspondance')) + '</div>\n</section>\n')
MOTIFS = ('<section aria-labelledby="motifs" class="v7-panel">\n' + EN.head('motifs', 'Motifs de rejet', '86 496 demandes rejetées. Cliquez sur un motif pour le détailler.') +
          '<div class="v7-pbody tq-col">\n' + inner(section('motifs')) + '</div>\n</section>\n')
DETAIL = ('<section aria-labelledby="detail" class="v7-panel">\n' + EN.head('detail', '{{cur.label}}, en détail', '{{cur.value}} demandes rejetées pour ce motif') +
          '<div class="v7-pbody tq-col">\n' + inner(section('detail')) + '</div>\n</section>\n')
ROW4 = '<div class="en-row2 tq-row4">\n' + STATUTS + REGLE + '</div>\n'
ROW5 = '<div class="en-row2 tq-row5">\n' + MOTIFS + DETAIL + '</div>\n'

# =============== 5. Types de demande ===============
_ty = section('types')
_ttab = re.search(r'<div role="table" aria-label="Autres types de demande".*?</sc-for>\n</div>\n', _ty, re.S).group(0)
_ttab = _ttab.replace('style="flex: 2 1 480px; min-width: 0; display: flex;', 'style="min-width: 0; display: flex;', 1)
TYPES = ('<section aria-labelledby="types" class="v7-panel">\n'
         + EN.head('types', 'Paquets par type de demande', 'Les nouvelles inscriptions représentent 99,1 % des paquets ; les autres types sont comparés entre eux.') +
         '<div class="tq-types">\n<div class="en-pre-main tq-tymain"><p class="en-big"><span class="en-bigv">3 249 758</span>'
         '<span class="en-bigu">nouvelles inscriptions, soit 99,1 % des paquets</span></p></div>\n'
         '<div class="v7-pbody">\n' + _ttab + '</div>\n</div>\n</section>\n')

BODY = TITLE + P1 + ROW2 + ETAPES + ROW4 + ROW5 + TYPES
for h in ('{{stages}}', '{{colTotals}}', '{{status}}', '{{mapping}}', '{{reasons}}', '{{cur.subs}}', '{{types}}', '{{cur.label}}'):
    assert h in BODY, h

CSS_TQ = (
    '.tq-p1cards{padding-bottom:40px}'
    '.tq-row2{grid-template-columns:minmax(0,1.25fr) minmax(0,1fr)}.tq-row4{grid-template-columns:minmax(0,1.3fr) minmax(0,1fr)}'
    '.tq-row5{grid-template-columns:minmax(0,1fr) minmax(0,1.4fr)}'
    '.tq-t4{grid-template-columns:minmax(120px,1fr) minmax(150px,1.3fr) minmax(130px,1.1fr) 90px}.tq-t4>span:nth-child(2),.tq-t4>span:nth-child(3){text-align:left !important}'
    '.tq-mut{font-size:12px;color:#4B5A6E}.tq-red{color:#8A1F1F}'
    '.tq-cl{list-style:none;margin:0;padding:0}'
    '.tq-c{display:grid;grid-template-columns:104px minmax(0,1fr);column-gap:14px;row-gap:2px;align-items:baseline;padding:12px 0;border-top:1px solid #EEF2F5}'
    '.tq-c:first-child{border-top:0}'
    '.tq-st{grid-row:1/span 2;align-self:start;justify-self:start;padding:3px 9px;border-radius:999px;font-size:11.5px;font-weight:600;white-space:nowrap}'
    '.tq-ko{background:#FCEBEB;color:#8A1F1F}.tq-warn{background:#FFF1CC;color:#6B4A00}.tq-ok{background:#E3F6EE;color:#0B6B47}'
    '.tq-cr{font-size:14px;font-weight:500;color:#071B35}.tq-cv{font-size:12.5px;color:#4B5A6E}'
    '.tq-col{display:flex;flex-direction:column;gap:16px}'
    '.tq-types{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2fr)}'
    '.tq-tymain{justify-content:center}'
    '@media (max-width:1100px){.tq-row2,.tq-row4,.tq-row5,.tq-types{grid-template-columns:minmax(0,1fr)}.tq-tymain{border-right:0;border-bottom:1px solid #E6EBF0}}'
    '@media (max-width:600px){.tq-c{grid-template-columns:minmax(0,1fr)}.tq-st{grid-row:auto;margin-bottom:4px}.tq-t4{grid-template-columns:minmax(104px,1.1fr) minmax(92px,1fr) 62px;gap:8px;font-size:12.5px;padding-left:2px;padding-right:2px}.tq-t4>span:nth-child(3){display:none}}'
)


def build():
    html = page('Qualité et technique', 'Technique.dc.html', OLD.FILTERS, BODY, SCRIPT, 3551, '')
    for blk in (bandeau('Technique.dc.html'), filters(OLD.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + V3.CSS9 + EN.CSS_EN + V5.CSS_AB + CSS_TQ + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
