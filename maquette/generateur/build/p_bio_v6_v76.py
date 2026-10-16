"""ABIS v6 (8 oct. 2026) : KPI strictement alignés sur le document IN Groupe « Reporting BI biométrique ABIS » v0.2 (23/01/2026).

Les 4 rapports du document, dans l'ordre de son chapitre 2, et seulement ses indicateurs :
1. Transactions ABIS : requêtes d'insertion (mosip.abis.insert), requêtes de déduplication (mosip.abis.identify).
2. Adjudication : requêtes reçues, cas traités (returnValue 1), HIT (count > 0), NO HIT (count 0),
   dossiers en attente = reçues − traités − en erreur.
3. Erreurs ABIS par type (returnValue 2) : insertion, identification, adjudication.
4. Qualité : score des biométries injectées (quality.log MBSS, RqType=IP) : visage, œil gauche, œil droit, 10 doigts (avec NBPK).
Retirés (absents du document) : part des inscriptions passées par l'ABIS, délais, requêtes sans réponse, vues par jour,
causes d'erreur, régions, agents, niveaux de qualité, histogrammes, centres. Filtre Région retiré (absent des logs ABIS).
Toujours des DONNÉES DE TEST.
"""
from common import *
import p_bio as B, p_main_v3 as V3, p_enrol_v5 as EN, p_bio_v5 as V5

nf, dec, pct, IC, scard = B.nf, B.dec, V5.pct, V5.IC, V5.scard

# =============== Données de test ===============
DEDUP = B.DEDUP                      # requêtes de déduplication : 3 158 734
ERR_INS, ERR_ID, ERR_ADJ = B.ERR_INS, B.ERR_ID, B.ERR_ADJ
REQ_INS = DEDUP + ERR_INS            # chaque insertion réussie est suivie d'une déduplication
ADJ_REQ, ADJ_TRT, HIT, NOHIT = B.ADJ_RECUS, B.ADJ_TRAITES, B.HIT, B.NOHIT
ADJ_ATT = ADJ_REQ - ADJ_TRT - ERR_ADJ
assert ADJ_TRT == HIT + NOHIT and ADJ_ATT == B.ADJ_ATTENTE == 2353
ERR_TOT = ERR_INS + ERR_ID + ERR_ADJ

# =============== Bandeau ===============
TITLE = ('<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 14px">\n'
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px">'
         '<h1 style="margin: 0 4px 0 0; font-size: 30px; font-weight: 600; letter-spacing: -0.015em; color: #FFFFFF">ABIS</h1>' + EN.FRESH
         + '</div>\n'
         '<form aria-label="Filtres appliqués à toute la page" style="display: flex; flex-wrap: wrap; gap: 10px">'
         + EN.pill('Période', ['Depuis le début', '7 derniers jours', '30 derniers jours', '90 derniers jours', 'Période personnalisée'], 150)
         + '</form>\n</div>\n')


def hero(icon, label, value, detail):
    return (f'<div class="v9-card en-card ab-hero">{IC[icon]}<span class="v9-body"><span class="v9-name">{label}</span>'
            f'<span class="v9-val">{value}</span><span class="v9-sub">{detail}</span></span></div>')


def split(label, parts):
    return (f'<div role="img" aria-label="{label} : ' + ', '.join(f'{l} {nf(n)}' for l, n, _ in parts) + '" class="en-split">'
            + ''.join(f'<span style="flex: {n} 1 0; background: {c}"></span>' for _, n, c in parts) + '</div>'
            '<div class="en-leg">' + ''.join(f'<span><i style="background: {c}"></i>{l} <strong>{nf(n)}</strong></span>' for l, n, c in parts) + '</div>')


# =============== 1. Transactions ABIS ===============
TRANS = ('<section aria-labelledby="transactions" class="v7-panel en-dev">\n' + BRACKETS
         + EN.head('transactions', 'Transactions ABIS', 'Requêtes envoyées par MOSIP à l’ABIS. Source : auditlog des 3 nœuds brs.') +
         '<div class="ab-heros">'
         + hero('db_in', 'Requêtes d’insertion', nf(REQ_INS), 'Enregistrement des biométries dans la base de l’ABIS')
         + hero('search', 'Requêtes de déduplication', nf(DEDUP), 'Recherche de doublons dans la base de l’ABIS')
         + '</div>\n</section>\n')

# =============== 2. Adjudication ===============
_adj = [('HIT', HIT, B.C_HIT), ('NO HIT', NOHIT, B.C_NOHIT), ('En attente', ADJ_ATT, B.C_WAIT), ('En erreur', ERR_ADJ, B.C_ERR)]
ADJ = ('<section aria-labelledby="adjudication" class="v7-panel">\n'
       + EN.head('adjudication', 'Adjudication', 'Dossiers envoyés par MOSIP à l’adjudication, où un agent tranche entre doublon et non-doublon.') +
       '<div class="en-pre">\n<div class="en-pre-main">'
       f'<p class="en-big"><span class="en-bigv">{nf(ADJ_REQ)}</span><span class="en-bigu">requêtes d’adjudication reçues par l’ABIS</span></p>'
       + split('Requêtes d’adjudication', _adj) +
       '<p class="ab-note">En attente = requêtes reçues − cas traités − requêtes en erreur.</p>'
       '</div>\n<div class="en-cards en-c2 en-pre-cards">'
       + scard('folder_ok', 'Cas d’adjudication traités', nf(ADJ_TRT), f'{pct(ADJ_TRT / ADJ_REQ * 100)} des requêtes reçues')
       + scard('wait', 'Dossiers en attente de traitement', nf(ADJ_ATT), f'{pct(ADJ_ATT / ADJ_REQ * 100)} des requêtes reçues')
       + scard('hit', 'Dossiers traités avec statut HIT', nf(HIT), f'Doublon confirmé : {pct(HIT / ADJ_TRT * 100)} des cas traités')
       + scard('user_ok', 'Dossiers traités NO HIT', nf(NOHIT), f'Aucun doublon : {pct(NOHIT / ADJ_TRT * 100)} des cas traités')
       + '</div>\n</div>\n</section>\n')

# =============== 3. Erreurs ABIS par type ===============
_err = [('Insertion', ERR_INS, '#8A1F1F'), ('Identification', ERR_ID, '#D03B3B'), ('Adjudication', ERR_ADJ, '#EC835A')]
ERREURS = ('<section aria-labelledby="erreurs" class="v7-panel">\n'
           + EN.head('erreurs', 'Erreurs ABIS', 'Réponses en erreur renvoyées par l’ABIS à MOSIP, par type de requête.') +
           '<div class="en-pre">\n<div class="en-pre-main">'
           f'<p class="en-big"><span class="en-bigv">{nf(ERR_TOT)}</span><span class="en-bigu">réponses en erreur</span></p>'
           + split('Erreurs ABIS par type', _err) +
           '</div>\n<div class="en-cards en-c3 en-pre-cards">'
           + scard('db_in', 'Erreurs d’insertion', nf(ERR_INS), f'{pct(ERR_INS / REQ_INS * 100, 2)} des requêtes d’insertion')
           + scard('search', 'Erreurs d’identification', nf(ERR_ID), f'{pct(ERR_ID / DEDUP * 100, 2)} des requêtes de déduplication')
           + scard('adj', 'Erreurs d’adjudication', nf(ERR_ADJ), f'{pct(ERR_ADJ / ADJ_REQ * 100, 2)} des requêtes d’adjudication')
           + '</div>\n</div>\n</section>\n')


# =============== 4. Qualité des données biométriques ===============
def qcard(icon, label, value, scale, detail, extra=''):
    return (f'<div class="v9-card en-card ab-qc">{IC[icon]}<span class="v9-body"><span class="v9-name">{label}</span>'
            f'<span class="v9-val">{dec(value)}<span class="v9-unit">sur {scale}</span></span>'
            f'<span aria-hidden="true" class="ab-scb"><span style="width: {value / scale * 100:.1f}%"></span></span>'
            f'<span class="v9-sub">{detail}</span>{extra}</span></div>')


def eye(name, v):
    return (f'<span class="ab-eye"><span>{name}</span><span aria-hidden="true" class="ab-scb ab-scs"><span style="width: {v:.1f}%; background: #2A78D6"></span></span>'
            f'<strong>{dec(v)}</strong></span>')


(_, OG), (_, OD) = B.EYES
IRIS = round((OG + OD) / 2, 1)
assert IRIS == B.Q_IRIS['score']
QUALITY = ('<section aria-labelledby="qualite" class="v7-panel">\n'
           + EN.head('qualite', 'Qualité des données biométriques',
                     'Score qualité moyen des biométries injectées dans l’ABIS. Source : quality.log des 2 nœuds MBSS (requêtes RqType=IP).') +
           '<div class="v7-pbody en-hebdo ab-qbody">\n<div class="en-cards ab-c3q">'
           + qcard('face', 'Face', B.Q_FACE['score'], 255, 'Score moyen')
           + qcard('iris', 'Iris', IRIS, 100, 'Score moyen des deux yeux',
                   '<span class="ab-eyes">' + eye('RightEye', OD) + eye('LeftEye', OG) + '</span>')
           + qcard('finger', 'Fingerprint', B.Q_FINGER['score'], 255, 'Moyenne des 10 doigts')
           + '</div>\n'
           '<div class="ab-fsec"><p class="en-tt">Fingerprint : score par doigt</p>\n<div class="ab-hands">'
           + ''.join(f'<div class="ab-hand"><p class="ab-handt">{main}</p><div class="ab-fing">'
                     + ''.join(f'<div class="ab-f"><span class="ab-fn">{d}</span><span class="ab-fv">{v}</span>'
                               f'<span aria-hidden="true" class="ab-fb"><span style="width: {v / 255 * 100:.1f}%; background: #013781"></span></span>'
                               f'<span class="ab-fk">NBPK {nb}</span></div>' for d, v, nb in doigts)
                     + '</div></div>' for main, doigts in B.DOIGTS.items())
           + '</div></div>\n</div>\n</section>\n')

BODY = TITLE + TRANS + ADJ + ERREURS + QUALITY
SCRIPT = '''class Component extends DCLogic {
  renderVals() {
    return {};
  }
}'''

CSS_AB6 = (
    '.ab-heros{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px 20px;padding:24px 28px 46px}'
    '.ab-hero{padding:22px 26px;gap:20px}.ab-hero>svg{width:56px;height:56px}.ab-hero .v9-name{font-size:15px}.ab-hero .v9-val{font-size:34px}'
    '.ab-c3q{grid-template-columns:repeat(3,minmax(0,1fr))}.ab-qc{align-items:flex-start}.ab-qc>svg{margin-top:2px}'
    '.ab-eyes{display:flex;flex-direction:column;gap:6px;margin-top:8px;padding-top:10px;border-top:1px solid #EEF2F5}'
    '.ab-eye{display:grid;grid-template-columns:68px minmax(0,1fr) 34px;align-items:center;gap:10px;font-size:12.5px;color:#4B5A6E}'
    '.ab-eye strong{font-weight:600;color:#071B35;text-align:right;font-variant-numeric:tabular-nums}.ab-scs{margin:0}'
    '.ab-scb{display:block;height:6px;margin:4px 0 2px;background:#EEF2F5;border-radius:3px}.ab-scb>span{display:block;height:6px;border-radius:3px;background:#013781}'
    '.ab-qbody{gap:22px}.ab-fsec{padding-top:20px;border-top:1px solid #E6EBF0}'
    '.ab-hands{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px 28px}'
    '@media (max-width:860px){.ab-c3q{grid-template-columns:minmax(0,1fr)}}'
    '@media (max-width:1100px){.ab-hands{grid-template-columns:minmax(0,1fr)}}'
    '@media (max-width:700px){.ab-heros{grid-template-columns:minmax(0,1fr);padding:16px 20px 40px}.ab-hero .v9-val{font-size:28px}.ab-hero>svg{width:44px;height:44px}}'

)


def build():
    html = page('ABIS', 'Biometrie.dc.html', B.FILTERS, BODY, SCRIPT, 1998, '')
    for blk in (bandeau('Biometrie.dc.html'), filters(B.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + V3.CSS9 + EN.CSS_EN + V5.CSS_AB + CSS_AB6 + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
