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
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px; align-self: stretch">'
         '<h1 style="margin: 0 4px 0 0; font-size: 30px; font-weight: 600; letter-spacing: -0.015em; color: #FFFFFF">ABIS</h1>' + EN.FRESH.replace('14/01/2026 à 11h42', '14/01/2026 à 11h40')
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
            '<div class="en-leg">' + ''.join(f'<span><i style="background: {c}"></i>{l}</span>' for l, n, c in parts) + '</div>')


# =============== 1. Transactions ABIS ===============
TRANS = ('<section aria-labelledby="transactions" class="v7-panel en-dev">\n' + BRACKETS
         + EN.head('transactions', 'Transactions ABIS', 'Requêtes envoyées par MOSIP à l’ABIS.') +
         '<div class="ab-heros">'
         + hero('db_in', 'Requêtes d’insertion', nf(REQ_INS), 'Enregistrement des biométries dans la base de l’ABIS')
         + hero('search', 'Requêtes de déduplication', nf(DEDUP), 'Recherche de doublons dans la base de l’ABIS')
         + '</div>\n<p class="v8-src ab-srct">Source : auditlog des 3 nœuds brs de l’ABIS.</p>\n</section>\n')

# =============== 2. Adjudication ===============
_adj = [('HIT', HIT, B.C_HIT), ('NO HIT', NOHIT, B.C_NOHIT), ('En attente', ADJ_ATT, B.C_WAIT), ('En erreur', ERR_ADJ, B.C_ERR)]
ADJ = ('<section aria-labelledby="adjudication" class="v7-panel">\n'
       + EN.head('adjudication', 'Adjudication', 'Dossiers envoyés par MOSIP à l’adjudication, où un agent tranche entre doublon et non-doublon.') +
       '<div class="en-pre">\n<div class="en-pre-main">'
       f'<p class="en-big"><span class="en-bigv">{nf(ADJ_REQ)}</span><span class="en-bigu">requêtes d’adjudication reçues par l’ABIS</span></p>'
       + split('Requêtes d’adjudication', _adj) +
       '<p class="ab-note">En attente : requêtes reçues, moins les cas traités et les requêtes en erreur.</p>'
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
# Niveaux Fingerprint selon le nombre de minuties (NBPK) : Faible < 16, Moyen 16 à 39, Excellent >= 40 ; exploitable = Moyen ou Excellent.
# Répartition par doigt (en % des captures du doigt) : données de test, cohérentes avec le NBPK moyen de chaque doigt.
LVL = [('Faible', '#EC835A'), ('Moyen', '#6DA7EC'), ('Excellent', '#013781')]
FP_LEVELS = {'Main droite': [(2.1, 38.4, 59.5), (1.8, 33.9, 64.3), (2.9, 46.2, 50.9), (2.6, 41.0, 56.4), (11.8, 76.5, 11.7)],
             'Main gauche': [(2.4, 43.1, 54.5), (2.0, 35.8, 62.2), (3.4, 50.3, 46.3), (3.1, 48.6, 48.3), (13.1, 77.2, 9.7)]}
for _h in FP_LEVELS.values():
    for _t in _h:
        assert abs(sum(_t) - 100) < 0.05, _t
_all = [t for h in FP_LEVELS.values() for t in h]
FP_TOT = [round(sum(t[i] for t in _all) / 10, 1) for i in range(3)]
FP_TOT[1] = round(100 - FP_TOT[0] - FP_TOT[2], 1)
FP_EXPL = round(100 - FP_TOT[0], 1)


def lbar(t, label):
    return (f'<div role="img" aria-label="{label} : ' + ', '.join(f'{n} {dec(v)} %' for (n, _), v in zip(LVL, t)) + '" class="ab-lbar">'
            + ''.join(f'<span title="{n} : {dec(v)} %" style="flex: {v} 1 0; background: {c}"></span>' for (n, c), v in zip(LVL, t)) + '</div>')


_frows = ''
for main, doigts in B.DOIGTS.items():
    _frows += (f'<div class="ab-hand"><p class="ab-handt">{main}</p>\n<div role="table" aria-label="Fingerprint, {main.lower()}" class="ab-ft">\n'
               '<div role="row" class="ab-fr ab-frh"><span role="columnheader">Doigt</span><span role="columnheader">Faible · Moyen · Excellent</span>'
               '<span role="columnheader">Exploitables</span><span role="columnheader">NBPK</span><span role="columnheader">Score</span></div>\n')
    for (d, v, nb), t in zip(doigts, FP_LEVELS[main]):
        ex = 100 - t[0]
        _frows += (f'<div role="row" class="ab-fr"><span role="rowheader">{d}</span><span role="cell">{lbar(t, d)}</span>'
                   f'<span role="cell" class="ab-fx{" ab-fxw" if ex < 90 else ""}">{dec(ex)} %</span><span role="cell">{nb}</span><span role="cell">{v}</span></div>\n')
    _frows += '</div>\n</div>\n'
FP_SEC = ('<div class="ab-fsec">\n<div class="v7-head ab-fhead"><div><h3 class="en-tt" style="margin: 0">Fingerprint : niveau de qualité et taux d’exploitabilité</h3>'
          '<p class="en-sub">Niveau de chaque doigt capturé selon son nombre de minuties (NBPK).</p></div></div>\n'
          '<div class="ab-fsum">\n<div class="ab-fkpi"><span class="ab-fkv">' + dec(FP_EXPL) + ' %</span>'
          '<span class="ab-fkl">des doigts capturés sont exploitables (niveau moyen ou excellent)</span></div>\n'
          '<div class="ab-fdist">' + lbar(FP_TOT, 'Fingerprint, tous doigts').replace('class="ab-lbar"', 'class="ab-lbar ab-lbig"', 1)
          + '<div class="en-leg">' + ''.join(f'<span><i style="background: {c}"></i>{n} <strong>{dec(v)} %</strong></span>' for (n, c), v in zip(LVL, FP_TOT)) + '</div>'
          '<p class="ab-fdef">Faible : moins de 16 minuties (sous le minimum recommandé à l’enrôlement, ISO/IEC 19794-2) · Moyen : 16 à 39 · Excellent : 40 et plus.</p></div>\n'
          '</div>\n<p class="en-tt ab-ftt">Taux d’exploitabilité par doigt</p>\n<div class="ab-hands">\n' + _frows + '</div>\n</div>\n')


QUALITY = ('<section aria-labelledby="qualite" class="v7-panel">\n'
           + EN.head('qualite', 'Qualité des données biométriques',
                     'Score qualité moyen des biométries injectées dans l’ABIS.') +
           '<div class="v7-pbody en-hebdo ab-qbody">\n<div class="en-cards ab-c3q">'
           + qcard('face', 'Face', B.Q_FACE['score'], 255, 'Score moyen')
           + qcard('iris', 'Iris', IRIS, 100, 'Score moyen des deux yeux',
                   '<span class="ab-eyes">' + eye('RightEye', OD) + eye('LeftEye', OG) + '</span>')
           + qcard('finger', 'Fingerprint', B.Q_FINGER['score'], 255, 'Moyenne des 10 doigts')
           + '</div>\n'
           + FP_SEC + '<p class="v8-src">Source : quality.log des 2 nœuds MBSS (requêtes RqType=IP).</p>\n</div>\n</section>\n')

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
    '.ab-fhead{padding:0 0 16px;border-bottom:0}'
    '.ab-fsum{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:16px 40px;align-items:center;padding:18px 22px;border-radius:10px;background:#F7F9FB}'
    '.ab-fkpi{display:flex;flex-direction:column;gap:2px}.ab-fkv{font-size:38px;font-weight:600;letter-spacing:-0.025em;line-height:1.1;color:#071B35;font-variant-numeric:tabular-nums}'
    '.ab-fkl{font-size:13px;color:#4B5A6E}.ab-fdist{display:flex;flex-direction:column;gap:10px;min-width:0}'
    '.ab-lbar{display:flex;gap:2px;height:12px;border-radius:3px;overflow:hidden;min-width:0}.ab-lbar>span{min-width:3px}.ab-lbig{height:16px;border-radius:4px}'
    '.ab-fdef{margin:0;font-size:12px;color:#4B5A6E}.ab-ftt{margin:22px 0 10px}'
    '.ab-ft{font-variant-numeric:tabular-nums}'
    '.ab-fr{display:grid;grid-template-columns:86px minmax(0,1fr) 84px 44px 44px;gap:12px;align-items:center;padding:9px 0;border-top:1px solid #EEF2F5;font-size:13.5px}'
    '.ab-fr>span:nth-child(n+3){text-align:right}.ab-fr>span:first-child{font-weight:500}'
    '.ab-frh{padding:4px 0 6px;border-top:0;font-size:12px;color:#4B5A6E}.ab-frh>span:first-child{font-weight:400}'
    '.ab-fx{font-weight:600;color:#071B35}.ab-fxw{color:#B4541F}'
    '@media (max-width:860px){.ab-c3q{grid-template-columns:minmax(0,1fr)}.ab-fsum{grid-template-columns:minmax(0,1fr)}}'
    '@media (max-width:520px){.ab-fr{grid-template-columns:72px minmax(0,1fr) 62px;gap:8px}.ab-fr>span:nth-child(n+4){display:none}}'
    '@media (max-width:1100px){.ab-hands{grid-template-columns:minmax(0,1fr)}}'
    '@media (max-width:700px){.ab-heros{grid-template-columns:minmax(0,1fr);padding:16px 20px 40px}.ab-hero .v9-val{font-size:28px}.ab-hero>svg{width:44px;height:44px}}'

)


def build():
    html = page('ABIS', 'Biometrie.dc.html', B.FILTERS, BODY, SCRIPT, 2328, '')
    for blk in (bandeau('Biometrie.dc.html'), filters(B.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + V3.CSS9 + EN.CSS_EN + V5.CSS_AB + CSS_AB6 + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
