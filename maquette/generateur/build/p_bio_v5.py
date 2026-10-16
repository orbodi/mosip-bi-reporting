"""ABIS v5 (7 oct. 2026) : refonte au langage de la Vue d'ensemble, de l'Enrôlement et de l'Impression des cartes.

- Titre, pastille de fraîcheur, pastille « Données de test » et filtres en pastilles dans le bandeau bleu.
- Recherche de doublons : chiffre principal, barre de couverture et 6 cartes au style v9 (crochets jaunes).
- Graphiques côte à côte dans des panneaux à en-tête ; survol = lecture de la semaine ou du mois.
- Adjudication : chiffre principal, barre HIT / NO HIT / en attente / erreurs et 6 cartes ; décisions et attente par semaine côte à côte.
- Qualité : 3 cartes de modalité, qualité par doigt et classement des centres côte à côte.
Toutes les valeurs sont des DONNÉES DE TEST (reprises de p_bio, cohérences vérifiées là-bas).
"""
import json
from common import *
import p_bio as B, p_main_v3 as V3, p_enrol_v5 as EN

nf, dec = B.nf, B.dec


def pct(x, d=1):
    return dec(x, d) + '\u00a0%'

INS, DEDUP, INSERT = B.INSCRIPTIONS, B.DEDUP, B.INSERT
C_HIT, C_NOHIT, C_ERR, C_WAIT = B.C_HIT, B.C_NOHIT, B.C_ERR, B.C_WAIT

# =============== Icônes (même style bicolore que les cartes v9) ===============
_N, _G1, _G2, _IA = EN._N, EN._G1, EN._G2, EN._IA
_FOLD = 'M5 12a3 3 0 0 1 3-3h10l4 5h18a3 3 0 0 1 3 3v20a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3z'
IC = dict(EN.IC)
IC.update({
    'db_in': (f'<svg {_IA}><path d="M7 12v22c0 3.3 6.3 6 14 6s14-2.7 14-6V12" fill="{_G1}"></path><ellipse cx="21" cy="12" rx="14" ry="6" fill="{_G2}"></ellipse>'
              '<path d="M7 23c0 3.3 6.3 6 14 6s14-2.7 14-6"></path><circle cx="37" cy="35" r="8" fill="#FFFFFF"></circle><path d="M37 31v8M33 35h8"></path></svg>'),
    'search': (f'<svg {_IA}><circle cx="21" cy="21" r="13" fill="{_G1}"></circle><path d="M21 8a13 13 0 0 0 0 26z" fill="{_G2}" stroke="none"></path>'
               '<circle cx="21" cy="21" r="13"></circle><path d="M15 21h12"></path><path d="m31 31 10 10" stroke-width="3"></path></svg>'),
    'adj': (f'<svg {_IA}><path d="M24 9v31M16 40h16M10 13h28"></path><circle cx="24" cy="8" r="2.6" fill="{_G2}"></circle>'
            f'<path d="M10 13 4.5 26M10 13l5.5 13M38 13l-5.5 13M38 13l5.5 13"></path>'
            f'<path d="M3.5 26a6.5 6.5 0 0 0 13 0z" fill="{_G2}"></path><path d="M31.5 26a6.5 6.5 0 0 0 13 0z" fill="{_G1}"></path></svg>'),
    'noresp': (f'<svg {_IA}><path d="M9 9h27a3 3 0 0 1 3 3v17a3 3 0 0 1-3 3H19l-8 7v-7H9a3 3 0 0 1-3-3V12a3 3 0 0 1 3-3z" fill="{_G1}"></path>'
               f'<circle cx="15" cy="20.5" r="1.7" fill="{_N}" stroke="none"></circle><circle cx="22" cy="20.5" r="1.7" fill="{_N}" stroke="none"></circle>'
               f'<circle cx="29" cy="20.5" r="1.7" fill="{_N}" stroke="none"></circle><circle cx="37" cy="35" r="8" fill="{_G2}"></circle><path d="M37 30.5v5M37 39v.3" stroke-width="2.4"></path></svg>'),
    'folder_ok': (f'<svg {_IA}><path d="{_FOLD}" fill="{_G1}" stroke="none"></path><path d="M5 12a3 3 0 0 1 3-3h10l4 5H5z" fill="{_G2}" stroke="none"></path>'
                  f'<path d="{_FOLD}"></path><path d="m17 27 5 5 9-9" stroke-width="2.4"></path></svg>'),
    'hit': (f'<svg {_IA}><circle cx="12.5" cy="17" r="5.5" fill="{_G2}"></circle><path d="M3 37c0-6.4 4.3-10.5 9.5-10.5S22 30.6 22 37z" fill="{_G2}"></path>'
            f'<circle cx="35.5" cy="17" r="5.5" fill="{_G1}"></circle><path d="M26 37c0-6.4 4.3-10.5 9.5-10.5S45 30.6 45 37z" fill="{_G1}"></path>'
            '<path d="M21.5 19.5h5M21.5 24h5" stroke-width="2.2"></path></svg>'),
    'finger': V3.ICONS9['abis'].replace('width="52" height="52"', 'width="44" height="44"'),
    'iris': (f'<svg {_IA}><path d="M3 24s8-13 21-13 21 13 21 13-8 13-21 13S3 24 3 24z" fill="{_G1}"></path><circle cx="24" cy="24" r="8" fill="{_G2}"></circle>'
             f'<circle cx="24" cy="24" r="3" fill="{_N}" stroke="none"></circle></svg>'),
    'face': (f'<svg {_IA}><path d="M5 14V8a3 3 0 0 1 3-3h6M34 5h6a3 3 0 0 1 3 3v6M43 34v6a3 3 0 0 1-3 3h-6M14 43H8a3 3 0 0 1-3-3v-6"></path>'
             f'<circle cx="24" cy="19" r="7" fill="{_G2}"></circle><path d="M12 37c1.8-6 6.4-9 12-9s10.2 3 12 9z" fill="{_G1}"></path></svg>'),
})


def scard(icon, label, value, detail):
    return (f'<div class="v9-card en-card">{IC[icon]}<span class="v9-body"><span class="v9-name">{label}</span>'
            f'<span class="v9-val">{value}</span><span class="v9-sub">{detail}</span></span></div>')


def leg(items):
    return '<div class="en-leg" style="margin-top: 0">' + ''.join(f'<span><i style="{st}"></i>{l}</span>' for l, st in items) + '</div>'


def sq(c):
    return f'background: {c}'


LINE_GREEN = 'width: 16px; height: 2px; border-radius: 0; background: #1BAF7A'

# =============== Bandeau ===============
TITLE = ('<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 14px">\n'
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px">'
         '<h1 style="margin: 0 4px 0 0; font-size: 30px; font-weight: 600; letter-spacing: -0.015em; color: #FFFFFF">ABIS</h1>' + EN.FRESH
         + '<span class="ab-test">Données de test</span></div>\n'
         '<form aria-label="Filtres appliqués à toute la page" style="display: flex; flex-wrap: wrap; gap: 10px">'
         + EN.pill('Période', ['Depuis le début', '7 derniers jours', '30 derniers jours', '90 derniers jours', 'Période personnalisée'], 150)
         + EN.pill('Région', ['Toutes les régions', 'Grand Lomé', 'Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'], 150)
         + EN.pill('Modalité', ['Toutes', 'Empreintes digitales', 'Iris', 'Visage'], 110)
         + '</form>\n</div>\n')

# =============== 1. Recherche de doublons ===============
_P = DEDUP / INS * 100
P1 = ('<section aria-labelledby="dedup" class="v7-panel en-dev">\n' + BRACKETS + EN.head('dedup', 'Recherche de doublons') +
      '<div class="en-pre">\n<div class="en-pre-main">'
      f'<p class="en-big"><span class="en-bigv">{nf(DEDUP)}</span><span class="en-bigu">recherches de doublons, soit {pct(_P)} des {nf(INS)} inscriptions</span></p>'
      f'<div role="img" aria-label="Inscriptions passées par l’ABIS {pct(_P)}, pas encore passées {pct(100 - _P)}" class="en-split">'
      f'<span style="flex: {DEDUP} 1 0; background: #013781"></span><span style="flex: {INS - DEDUP} 1 0; background: #6DA7EC"></span></div>'
      '<div class="en-leg">'
      f'<span><i style="background: #013781"></i>Passées par l’ABIS <strong>{nf(DEDUP)}</strong></span>'
      f'<span><i style="background: #6DA7EC"></i>Pas encore passées <strong>{nf(INS - DEDUP)}</strong></span></div>'
      '</div>\n<div class="en-cards en-c3 en-pre-cards ab-p1cards">'
      + scard('db_in', 'Insérées dans la base', nf(INSERT), f'{pct(INSERT / DEDUP * 100)} des recherches')
      + scard('search', 'Recherches sans insertion', nf(DEDUP - INSERT), 'Doublons, dossiers en cours ou en erreur')
      + scard('adj', 'Envoyées en adjudication', nf(B.ADJ_RECUS), f'{pct(B.ADJ_RECUS / DEDUP * 100)} des recherches')
      + scard('delai', 'Délai médian de déduplication', '41 s', '90 % en moins de 3 min 12 s')
      + scard('echec', 'Erreurs ABIS', nf(B.ERR_ID + B.ERR_INS), f'Sur {nf(DEDUP + INSERT)} requêtes')
      + scard('noresp', 'Requêtes sans réponse', nf(B.SANS_REPONSE), f'Dont {nf(B.SANS_REPONSE_24H)} depuis plus de 24 h')
      + '</div>\n</div>\n</section>\n')


# =============== 2. Requêtes par mois + jours de la semaine ===============
def yaxis(labels, width):
    n = len(labels) - 1
    return (f'<div aria-hidden="true" style="position: relative; width: {width}px; height: 220px; font-size: 12px; color: #4B5A6E; font-variant-numeric: tabular-nums; flex-shrink: 0">'
            + ''.join(f'<span style="position: absolute; right: 0; top: {i * 220 / n - 9:.1f}px">{l}</span>' for i, l in enumerate(labels)) + '</div>\n')


def plot_open(n_grid, min_w, axis):
    return ('<div style="overflow-x: auto; padding-top: 10px">\n'
            f'<div style="min-width: {min_w}px; display: flex; gap: 10px">\n' + axis +
            '<div style="flex-grow: 1; min-width: 0">\n'
            f'<div style="position: relative; height: 220px; border-bottom: 1px solid #9AA7B5; background-image: linear-gradient(#E6EBEF 1px, transparent 1px); background-size: 100% {220 / n_grid:.2f}px">\n'
            '<div style="position: absolute; top: 0; right: 0; bottom: 0; left: 0; display: flex; align-items: flex-end">\n')


def xlabels(lst, var, inner):
    return ('<div aria-hidden="true" style="display: flex; margin-top: 6px; font-size: 12px; line-height: 1.3; color: #4B5A6E; font-variant-numeric: tabular-nums">\n'
            f'<sc-for list="{{{{{lst}}}}}" as="{var}" hint-placeholder-count="12"><span style="flex: 1 1 0; text-align: center; white-space: nowrap">{inner}</span></sc-for>\n</div>\n')


MONTH_CHART = ('<p aria-live="polite" class="en-read">{{monRead}}</p>\n'
               + plot_open(3, 520, yaxis(['300 000', '200 000', '100 000', '0'], 56)) +
               '<sc-for list="{{months}}" as="m" hint-placeholder-count="14">\n'
               '<button type="button" onMouseEnter="{{m.enter}}" onFocus="{{m.enter}}" aria-label="{{m.aria}}" class="ab-vb" style="background: {{m.band}}">'
               '<span style="width: min(26px, 62%); height: {{m.h}}px; background: {{m.bg}}; opacity: {{m.op}}; border-radius: 4px 4px 0 0"></span></button>\n'
               '</sc-for>\n</div>\n'
               '<svg viewBox="0 0 1400 220" preserveAspectRatio="none" aria-hidden="true" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: visible; pointer-events: none">'
               '<polyline points="{{monLine}}" style="fill: none; stroke: #1BAF7A; stroke-width: 2px; stroke-linejoin: round; stroke-linecap: round; vector-effect: non-scaling-stroke"></polyline></svg>\n'
               '</div>\n'
               + xlabels('months', 'm', '{{m.label}}<br><strong style="font-weight: 600; color: #071B35">{{m.year}}</strong>')
               + '</div>\n</div>\n</div>\n'
               '<p class="ab-note">Janvier 2026 : du 1er au 14 (barre plus claire).</p>\n')
MONTHS = ('<section aria-labelledby="mois" class="v7-panel">\n'
          + EN.head('mois', 'Requêtes ABIS par mois', 'De décembre 2024 à janvier 2026.', leg([('Recherches de doublons', sq('#2A78D6')), ('Insertions', LINE_GREEN)])) +
          '<div class="v7-pbody en-hebdo">\n' + MONTH_CHART + '</div>\n</section>\n')

_wd = [[l.capitalize(), round(DEDUP * p / 100)] for _, l, p in B.JOURS]
_wd[0][1] += DEDUP - sum(v for _, v in _wd)
assert sum(v for _, v in _wd) == DEDUP
_wmax = max(v for _, v in _wd)
_we = _wd[5][1] + _wd[6][1]
WEEKDAYS = ('<section aria-labelledby="jours" class="v7-panel">\n'
            + EN.head('jours', 'Recherches par jour de la semaine', 'Recherches de doublons, depuis le début.') +
            '<div class="v7-pbody en-hebdo">\n<div role="table" aria-label="Recherches de doublons par jour de la semaine" class="ab-hrows">\n'
            + ''.join(f'<div role="row" class="ab-hrow"><span role="rowheader" class="ab-hl">{l}</span>'
                      f'<span role="cell" class="ab-hb"><span style="width: {v / _wmax * 100:.1f}%"></span></span><strong role="cell">{nf(v)}</strong></div>\n' for l, v in _wd)
            + f'</div>\n<p class="ab-note">Samedi et dimanche : {nf(_we)} recherches, soit {pct(_we / DEDUP * 100)} du total.</p>\n</div>\n</section>\n')
ROW_REQ = '<div class="en-row2 ab-row3">\n' + MONTHS + WEEKDAYS + '</div>\n'


# =============== 3. Détail par jour ===============
def table(label, cls, min_w, header, rows, total=None):
    def row(cells, extra='', role='cell'):
        out = f'<div role="row" class="ab-tr {cls}{extra}">'
        for i, c in enumerate(cells):
            r = 'columnheader' if role == 'columnheader' else ('rowheader' if i == 0 else 'cell')
            out += f'<span role="{r}">{c}</span>'
        return out + '</div>\n'
    return (f'<div class="ab-tw"><div role="table" aria-label="{label}" class="ab-table" style="min-width: {min_w}px">\n'
            + row(header, ' ab-th', 'columnheader') + ''.join(row(r) for r in rows) + (row(total, ' ab-tot') if total else '') + '</div></div>\n')


_ta, _tb, _te = (sum(d[i] for d in B.DAYS) for i in (1, 2, 3))
DETAIL = ('<section aria-labelledby="detail-jour" class="v7-panel">\n' + EN.head('detail-jour', 'Détail des requêtes par jour', 'Sept derniers jours, toutes les zones.') +
          '<div class="v7-pbody ab-tpad">\n'
          + table('Requêtes ABIS par jour', 'ab-t6', 640, ['Jour', 'Recherches de doublons', 'Insertions', 'Sans insertion', 'Erreurs', 'Délai médian'],
                  [[d, nf(a), nf(b), nf(a - b), nf(e), f'{s} s'] for d, a, b, e, s in B.DAYS],
                  ['Total, 7 jours', nf(_ta), nf(_tb), nf(_ta - _tb), nf(_te), '42 s'])
          + '</div>\n</section>\n')

# =============== 4. Erreurs par type et par cause ===============
_causes = sorted(B.CAUSES, key=lambda c: -(c[1] + c[2] + c[3]))
ERREURS = ('<section aria-labelledby="erreurs" class="v7-panel">\n' + EN.head('erreurs', 'Erreurs ABIS par type et par cause', 'Réponses en erreur renvoyées par l’ABIS à MOSIP.') +
           '<div class="ab-err">\n<div class="ab-errc">'
           + scard('db_in', 'Erreurs d’insertion', nf(B.ERR_INS), f'{pct(B.ERR_INS / INSERT * 100, 2)} des insertions')
           + scard('search', 'Erreurs de déduplication', nf(B.ERR_ID), f'{pct(B.ERR_ID / DEDUP * 100, 2)} des recherches')
           + scard('adj', 'Erreurs d’adjudication', nf(B.ERR_ADJ), f'{pct(B.ERR_ADJ / B.ADJ_RECUS * 100, 2)} des dossiers reçus')
           + '</div>\n<div class="ab-errt">\n<p class="en-tt" id="causes">Erreurs par cause</p>\n'
           + table('Erreurs ABIS par cause', 'ab-t5c', 600, ['Cause', 'Insertion', 'Déduplication', 'Adjudication', 'Total'],
                   [[c, nf(a), nf(b), nf(d), f'<strong>{nf(a + b + d)}</strong>'] for c, a, b, d in _causes],
                   ['Total', nf(B.ERR_INS), nf(B.ERR_ID), nf(B.ERR_ADJ), nf(B.ERR_INS + B.ERR_ID + B.ERR_ADJ)])
           + '</div>\n</div>\n</section>\n')

# =============== 5. Adjudication ===============
_R = B.ADJ_RECUS
_parts = [('HIT', B.HIT, C_HIT), ('NO HIT', B.NOHIT, C_NOHIT), ('En attente', B.ADJ_ATTENTE, C_WAIT), ('En erreur', B.ERR_ADJ, C_ERR)]
ADJ = ('<section aria-labelledby="adjudication" class="v7-panel">\n' + EN.head('adjudication', 'Adjudication des doublons', 'Un agent tranche quand l’ABIS signale une ressemblance.') +
       '<div class="en-pre">\n<div class="en-pre-main">'
       f'<p class="en-big"><span class="en-bigv">{nf(_R)}</span><span class="en-bigu">dossiers reçus en adjudication, soit {pct(_R / DEDUP * 100)} des recherches de doublons</span></p>'
       '<div role="img" aria-label="Dossiers reçus : ' + ', '.join(f'{l} {nf(n)}' for l, n, _ in _parts) + '" class="en-split">'
       + ''.join(f'<span style="flex: {n} 1 0; background: {c}"></span>' for _, n, c in _parts) + '</div>'
       '<div class="en-leg">' + ''.join(f'<span><i style="background: {c}"></i>{l} <strong>{nf(n)}</strong></span>' for l, n, c in _parts) + '</div>'
       '</div>\n<div class="en-cards en-c3 en-pre-cards">'
       + scard('folder_ok', 'Dossiers traités', nf(B.ADJ_TRAITES), f'Taux de traitement {pct(B.ADJ_TRAITES / (B.ADJ_TRAITES + B.ADJ_ATTENTE) * 100)}')
       + scard('hit', 'HIT : doublon confirmé', nf(B.HIT), f'{pct(B.HIT / B.ADJ_TRAITES * 100)} des dossiers traités')
       + scard('user_ok', 'NO HIT : pas de doublon', nf(B.NOHIT), f'{pct(B.NOHIT / B.ADJ_TRAITES * 100)} des dossiers traités')
       + scard('wait', 'En attente d’un agent', nf(B.ADJ_ATTENTE), f'Dont {nf(B.ADJ_ATTENTE_7J)} depuis plus de 7 jours')
       + scard('clock', 'Délai médian de décision', '2,6 jours', '90 % en moins de 9 jours')
       + scard('people', 'Candidats examinés', '1,7', 'Par dossier, en moyenne')
       + '</div>\n</div>\n</section>\n')

DEC_CHART = ('<p aria-live="polite" class="en-read" style="border-left-color: #D03B3B">{{decRead}}</p>\n'
             + plot_open(4, 380, yaxis(['1 000', '750', '500', '250', '0'], 40)) +
             '<sc-for list="{{decW}}" as="d" hint-placeholder-count="12">\n'
             '<button type="button" onMouseEnter="{{d.enter}}" onFocus="{{d.enter}}" aria-label="{{d.aria}}" class="ab-vb" style="background: {{d.band}}">'
             '<span class="ab-stk"><span style="height: {{d.hE}}px; background: #EC835A; border-radius: 3px 3px 0 0"></span>'
             '<span style="height: {{d.hN}}px; background: #2A78D6; border-top: 1px solid #FFFFFF"></span>'
             '<span style="height: {{d.hH}}px; background: #D03B3B; border-top: 1px solid #FFFFFF"></span></span></button>\n'
             '</sc-for>\n</div>\n</div>\n'
             + xlabels('decW', 'd', '{{d.label}}') + '</div>\n</div>\n</div>\n')
WAIT_CHART = ('<p aria-live="polite" class="en-read" style="border-left-color: #FAB219">{{waitRead}}</p>\n'
              + plot_open(5, 380, yaxis(['2 500', '2 000', '1 500', '1 000', '500', '0'], 40)) +
              '<sc-for list="{{waitW}}" as="q" hint-placeholder-count="12">\n'
              '<button type="button" onMouseEnter="{{q.enter}}" onFocus="{{q.enter}}" aria-label="{{q.aria}}" class="ab-vb" style="background: {{q.band}}">'
              '<span style="width: min(22px, 60%); height: {{q.h}}px; background: {{q.bg}}; border-radius: 4px 4px 0 0"></span></button>\n'
              '</sc-for>\n</div>\n</div>\n'
              + xlabels('waitW', 'q', '{{q.label}}') + '</div>\n</div>\n</div>\n')
DECISIONS = ('<section aria-labelledby="decisions" class="v7-panel">\n'
             + EN.head('decisions', 'Décisions par semaine', '12 dernières semaines complètes.', leg([('HIT', sq(C_HIT)), ('NO HIT', sq(C_NOHIT)), ('Erreurs', sq(C_ERR))])) +
             '<div class="v7-pbody en-hebdo">\n' + DEC_CHART + '</div>\n</section>\n')
ATTENTE = ('<section aria-labelledby="attente" class="v7-panel">\n'
           + EN.head('attente', 'Dossiers en attente en fin de semaine', 'Mêmes 12 semaines.') +
           '<div class="v7-pbody en-hebdo">\n' + WAIT_CHART + '</div>\n</section>\n')
ROW_DEC = '<div class="en-row2 ab-row2">\n' + DECISIONS + ATTENTE + '</div>\n'

_regs = sorted(B.REGIONS, key=lambda r: -r[1])
REGIONS = ('<section aria-labelledby="adj-regions" class="v7-panel">\n' + EN.head('adj-regions', 'Dossiers par région', 'Dossiers d’adjudication reçus depuis le début.') +
           '<div class="v7-pbody ab-tpad">\n'
           + table('Dossiers d’adjudication par région', 'ab-t7', 470, ['Région', 'Reçus', 'HIT', 'NO HIT', 'En attente', 'Erreurs', 'Délai médian'],
                   [[r[0], nf(r[1]), nf(r[7]), nf(r[4] - r[7]), nf(r[2]), nf(r[3]), f'{dec(r[6])} j'] for r in _regs],
                   ['Togo', nf(B.ADJ_RECUS), nf(B.HIT), nf(B.NOHIT), nf(B.ADJ_ATTENTE), nf(B.ERR_ADJ), '2,6 j'])
           + '</div>\n</section>\n')
AGENTS = ('<section aria-labelledby="agents" class="v7-panel">\n' + EN.head('agents', 'Activité des agents d’adjudication', 'Agents pseudonymisés, classés par dossiers traités.') +
          '<div class="v7-pbody ab-tpad">\n'
          + table('Activité des agents d’adjudication', 'ab-t5', 440, ['Agent', 'Dossiers traités', 'HIT', 'NO HIT', 'Délai médian'],
                  [[a[0], nf(a[1]), nf(a[4]), nf(a[1] - a[4]), f'{dec(a[3])} j'] for a in B.AGENTS],
                  ['Total', nf(B.ADJ_TRAITES), nf(B.HIT), nf(B.NOHIT), '2,6 j'])
          + '</div>\n</section>\n')
ROW_AG = '<div class="en-row2 ab-row2">\n' + REGIONS + AGENTS + '</div>\n'

# =============== 6. Qualité des captures ===============
_LV = [('Faible', '#B7D3F6'), ('Moyen', '#6DA7EC'), ('Excellent', '#184F95')]


def modality(icon, name, q, extra=''):
    seg = ''.join(f'<span title="{l} : {v} %" style="flex: {v} 1 0; background: {c}"></span>' for (l, c), v in zip(_LV, q['levels']) if v)
    lg = ''.join(f'<span><i style="background: {c}"></i>{l} <strong>{v} %</strong></span>' for (l, c), v in zip(_LV, q['levels']) if v)
    return (f'<div class="ab-mod">\n<div class="ab-modh">{IC[icon]}<h3 class="v9-name">{name}</h3></div>\n'
            f'<p class="ab-modv"><strong>{q["levels"][2]} %</strong>de captures excellentes</p>\n'
            f'<div role="img" aria-label="{name} : ' + ', '.join(f'{l} {v} %' for (l, _), v in zip(_LV, q['levels']) if v) + f'" class="en-split">{seg}</div>\n'
            f'<div class="en-leg">{lg}</div>\n'
            '<div class="ab-modb">\n' + B.kv('Score moyen', dec(q['score'])) + '\n' + B.hist(q, name) + '\n'
            f'<div class="ab-mm"><span>min {q["smin"]}</span><span>max {q["smax"]}</span></div>\n' + extra + '</div>\n</div>\n')


QUALITY = ('<section aria-labelledby="qualite" class="v7-panel">\n'
           + EN.head('qualite', 'Qualité des captures biométriques', 'Niveaux de qualité, score moyen et répartition des scores. Le trait marque la moyenne.',
                     '<span class="ab-last">Dernière capture le 14/01/2026 à 11h37</span>') +
           '<div class="v7-pbody ab-mods">\n'
           + modality('finger', 'Empreintes digitales', B.Q_FINGER, B.FINGER_EXTRA)
           + modality('iris', 'Iris', B.Q_IRIS, B.IRIS_EXTRA)
           + modality('face', 'Visage', B.Q_FACE)
           + '</div>\n</section>\n')

_FLEG = [('110 et plus', '#184F95'), ('95 à 110', '#2A78D6'), ('80 à 95', '#6DA7EC'), ('Moins de 80', '#B7D3F6')]
DOIGTS = ('<section aria-labelledby="doigts" class="v7-panel">\n' + EN.head('doigts', 'Empreintes : qualité par doigt', 'Score moyen de 0 à 255 et indice NBPK, par doigt.') +
          '<div class="v7-pbody en-hebdo">\n' + leg([(l, sq(c)) for l, c in _FLEG])
          + ''.join(f'<div class="ab-hand"><p class="ab-handt">{main}</p><div class="ab-fing">'
                    + ''.join(f'<div class="ab-f"><span class="ab-fn">{d}</span><span class="ab-fv">{v}</span>'
                              f'<span aria-hidden="true" class="ab-fb"><span style="width: {v / 255 * 100:.1f}%; background: {B.finger_color(v)}"></span></span>'
                              f'<span class="ab-fk">NBPK {nb}</span></div>' for d, v, nb in doigts)
                    + '</div></div>\n' for main, doigts in B.DOIGTS.items())
          + '</div>\n</section>\n')

TABS = ('<div role="group" aria-label="Choisir une modalité" class="en-tabs">'
        '<sc-for list="{{modTabs}}" as="m" hint-placeholder-count="3">'
        '<button type="button" onClick="{{m.pick}}" aria-pressed="{{m.pressed}}" style="min-height: 36px; padding: 0 12px; border: 0; border-radius: 6px; '
        'background: {{m.bg}}; color: {{m.fg}}; font-family: inherit; font-size: 13px; font-weight: 600; cursor: pointer; box-shadow: {{m.shadow}}">{{m.label}}</button>'
        '</sc-for></div>')
CENTRES = ('<section aria-labelledby="centres-qualite" class="v7-panel">\n'
           + EN.head('centres-qualite', 'Centres où la qualité est la plus basse', '{{modLabel}}, de la plus faible part de captures excellentes à la plus forte.', TABS) +
           '<div class="v7-pbody ab-cent">\n<div role="table" aria-label="Qualité des captures par centre" style="font-variant-numeric: tabular-nums">\n'
           '<div role="row" class="ab-rk ab-rkh"><span role="columnheader">Rang</span><span role="columnheader">Centre</span>'
           '<span role="columnheader" style="text-align: right">Captures excellentes</span></div>\n'
           '<sc-for list="{{centres}}" as="c" hint-placeholder-count="6">\n'
           '<div role="row" class="ab-rk"><span role="cell" class="ab-rkn">{{c.rank}}</span>'
           '<span role="rowheader" class="ab-rkc"><span>{{c.name}}</span><span>{{c.place}}</span></span>'
           '<span role="cell" class="ab-rkm"><strong>{{c.exc}}</strong><span>{{c.sub}}</span></span></div>\n'
           '</sc-for>\n</div>\n</div>\n</section>\n')
ROW_Q = '<div class="en-row2 ab-row2 ab-rowq">\n' + DOIGTS + CENTRES + '</div>\n'

BODY = TITLE + P1 + ROW_REQ + DETAIL + ERREURS + ADJ + ROW_DEC + ROW_AG + QUALITY + ROW_Q

# =============== Script ===============
_MOIS_LONG = ['Décembre 2024', 'Janvier 2025', 'Février 2025', 'Mars 2025', 'Avril 2025', 'Mai 2025', 'Juin 2025', 'Juillet 2025',
              'Août 2025', 'Septembre 2025', 'Octobre 2025', 'Novembre 2025', 'Décembre 2025', 'Janvier 2026']
_mo = [[m, B.ANNEES.get(i, ''), d, s, _MOIS_LONG[i]] for i, (m, d, s) in enumerate(zip(B.MOIS, B.M_DEDUP, B.M_INS))]
_MN = {'01': 'janvier', '10': 'octobre', '11': 'novembre', '12': 'décembre'}


def _wlong(s):
    d, m = s.split('/')
    d = int(d)
    return ('1er' if d == 1 else str(d)) + ' ' + _MN[m]


_sw = [[s, h, n, e, w, _wlong(s)] for s, h, n, e, w in zip(B.SEMAINES, B.W_HIT, B.W_NOHIT, B.W_ERR, B.W_WAIT)]
assert max(h + n + e for _, h, n, e, _, _ in _sw) < 1000 and max(B.W_WAIT) < 2500 and max(B.M_DEDUP) < 300000
JS = f'''    // requêtes ABIS par mois : barres = recherches de doublons, courbe = insertions
    const mo = {json.dumps(_mo, ensure_ascii=False)};
    const hovM = typeof st.hoverM === 'number' ? st.hoverM : mo.length - 2;
    const MH = 220, MM = 300000;
    const months = mo.map((m, i) => ({{ label: m[0], year: m[1], h: (m[2] / MM * MH).toFixed(1),
      bg: i === hovM ? '#1C5CAB' : '#2A78D6', op: i === mo.length - 1 ? '0.5' : '1',
      band: i === hovM ? 'rgba(42,120,214,0.07)' : 'transparent',
      aria: m[4] + ' : ' + nf(m[2]) + ' recherches de doublons, ' + nf(m[3]) + ' insertions',
      enter: () => this.setState({{ hoverM: i }}) }}));
    const hm = mo[hovM];
    const monRead = hm[4] + (hovM === mo.length - 1 ? ' (du 1er au 14)' : '') + ' : ' + nf(hm[2]) + ' recherches de doublons, ' + nf(hm[3]) + ' insertions.';
    const monLine = mo.map((m, i) => ((i + 0.5) * 100).toFixed(1) + ',' + (MH - m[3] / MM * MH).toFixed(1)).join(' ');
    // adjudication par semaine : décisions et dossiers en attente (survol partagé entre les deux graphiques)
    const sw = {json.dumps(_sw, ensure_ascii=False)};
    const hovD = typeof st.hoverD === 'number' ? st.hoverD : sw.length - 1;
    const DM = 1000, QM = 2500;
    const decW = sw.map((w, i) => ({{ label: i % 2 === 0 ? w[0] : '', hH: (w[1] / DM * MH).toFixed(1), hN: (w[2] / DM * MH).toFixed(1),
      hE: Math.max(w[3] / DM * MH, 2).toFixed(1), band: i === hovD ? 'rgba(1,55,129,0.07)' : 'transparent',
      aria: 'Semaine du ' + w[5] + ' : ' + w[1] + ' HIT, ' + w[2] + ' NO HIT, ' + w[3] + ' erreurs',
      enter: () => this.setState({{ hoverD: i }}) }}));
    const waitW = sw.map((w, i) => ({{ label: i % 2 === 0 ? w[0] : '', h: (w[4] / QM * MH).toFixed(1), bg: i === hovD ? '#C98A00' : '#FAB219',
      band: i === hovD ? 'rgba(250,178,25,0.10)' : 'transparent',
      aria: 'Fin de la semaine du ' + w[5] + ' : ' + nf(w[4]) + ' dossiers en attente',
      enter: () => this.setState({{ hoverD: i }}) }}));
    const hd = sw[hovD];
    const decRead = 'Semaine du ' + hd[5] + ' : ' + nf(hd[1] + hd[2] + hd[3]) + ' décisions, dont ' + hd[1] + ' HIT, ' + hd[2] + ' NO HIT et ' + hd[3] + ' erreurs.';
    const waitRead = 'Fin de la semaine du ' + hd[5] + ' : ' + nf(hd[4]) + ' dossiers en attente d’un agent.';
'''
SCRIPT = B.SCRIPT


def swap(old, new):
    global SCRIPT
    assert SCRIPT.count(old) == 1, old[:70]
    SCRIPT = SCRIPT.replace(old, new)


swap("""    const centres = C.map((c) => ({ name: c[0], place: c[1], n: nf(c[2]), exc: pct(c[idx][0]), w: c[idx][0].toFixed(1),
      weight: c[idx][0] < 80 ? '600' : '400', low: pct(c[idx][1]) })).sort((a, b) => parseFloat(a.w) - parseFloat(b.w));""",
     """    const centres = C.slice().sort((a, b) => a[idx][0] - b[idx][0]).map((c, i) => ({ rank: String(i + 1), name: c[0], place: c[1],
      exc: pct(c[idx][0]), sub: nf(c[2]) + ' captures, dont ' + nf(c[2] * c[idx][1] / 100) + ' faibles' }));""")
swap("bg: k === mod ? '#FFFFFF' : 'transparent', shadow: k === mod ? '0 1px 2px rgba(7, 27, 53, 0.15)' : 'none',",
     "bg: k === mod ? '#FFFFFF' : 'transparent', fg: k === mod ? '#071B35' : '#4B5A6E', shadow: k === mod ? '0 0 0 1px #DCE3E9' : 'none',")
swap("    return { centres: centres, modTabs: modTabs, modLabel: labels[mod] };",
     JS + "    return { centres: centres, modTabs: modTabs, modLabel: labels[mod], months: months, monRead: monRead, monLine: monLine,\n"
          "      decW: decW, waitW: waitW, decRead: decRead, waitRead: waitRead };")
for h in ('{{monRead}}', '{{months}}', '{{monLine}}', '{{decW}}', '{{waitW}}', '{{decRead}}', '{{waitRead}}', '{{centres}}', '{{modTabs}}', '{{modLabel}}'):
    assert h in BODY, h

CSS_AB = (
    '.ab-test{display:inline-flex;align-items:center;padding:6px 12px;border-radius:999px;background:#FCBA21;color:#071B35;font-size:13px;font-weight:600;white-space:nowrap}'
    '.ab-p1cards{padding-bottom:40px}'
    '.ab-row3{grid-template-columns:minmax(0,1.7fr) minmax(0,1fr)}.ab-row2{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}'
    '.ab-vb{flex:1 1 0;height:100%;display:flex;align-items:flex-end;justify-content:center;padding:0;border:0;cursor:default}'
    '.ab-stk{display:flex;flex-direction:column;width:min(22px,60%)}.ab-stk>span{display:block}'
    '.ab-note{margin:0;padding-top:12px;border-top:1px solid #E6EBF0;font-size:13px;color:#4B5A6E}'
    '.ab-hrows{display:flex;flex-direction:column;gap:16px;padding-top:4px}'
    '.ab-hrow{display:grid;grid-template-columns:84px minmax(0,1fr) 74px;gap:14px;align-items:center}'
    '.ab-hl{font-size:13px;font-weight:500}.ab-hb{height:16px;background:#EEF2F5;border-radius:0 4px 4px 0}'
    '.ab-hb>span{display:block;height:16px;background:#013781;border-radius:0 4px 4px 0}'
    '.ab-hrow strong{text-align:right;font-weight:600;font-variant-numeric:tabular-nums}'
    '.ab-tpad{padding-top:12px}.ab-tw{overflow-x:auto}.ab-table{font-variant-numeric:tabular-nums}'
    '.ab-tr{display:grid;gap:12px;align-items:center;padding:11px 8px;border-top:1px solid #EEF2F5}.ab-tr>span:not(:first-child){text-align:right}'
    '.ab-th{align-items:end;padding-top:6px;padding-bottom:8px;border-top:0;font-size:12px;line-height:1.35;color:#4B5A6E}'
    '.ab-tot{border-top:1px solid #C5CFDA;font-weight:600}.ab-tr strong{font-weight:600}'
    '.ab-t6{grid-template-columns:minmax(170px,1.5fr) repeat(5,minmax(80px,1fr))}'
    '.ab-t5c{grid-template-columns:minmax(200px,2.2fr) repeat(4,minmax(78px,1fr))}'
    '.ab-t7{grid-template-columns:minmax(88px,1.3fr) repeat(6,minmax(50px,1fr));gap:10px}'
    '.ab-t5{grid-template-columns:minmax(80px,1fr) repeat(4,minmax(66px,1fr))}'
    '.ab-err{display:grid;grid-template-columns:minmax(0,340px) minmax(0,1fr)}'
    '.ab-errc{padding:24px 28px 28px;display:flex;flex-direction:column;gap:14px;border-right:1px solid #E6EBF0}'
    '.ab-errt{padding:20px 28px 24px;min-width:0}'
    '.ab-last{font-size:13px;color:#4B5A6E}'
    '.ab-mods{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px 20px}'
    '.ab-mod{min-width:0;padding:20px 22px;border:1px solid #F5D77E;border-radius:10px;box-shadow:0 2px 6px rgba(7,27,53,.06);display:flex;flex-direction:column;gap:12px}'
    '.ab-modh{display:flex;align-items:center;gap:12px}.ab-modh .v9-name{font-size:16px}'
    '.ab-modv{margin:0;display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 10px;font-size:13px;color:#4B5A6E}'
    '.ab-modv strong{font-size:32px;font-weight:600;letter-spacing:-0.02em;line-height:1.1;color:#071B35}'
    '.ab-modb{padding-top:12px;border-top:1px solid #EEF2F5;display:flex;flex-direction:column;gap:8px}'
    '.ab-mm{display:flex;justify-content:space-between;font-size:12px;color:#4B5A6E;font-variant-numeric:tabular-nums}'
    '.ab-hand{display:flex;flex-direction:column;gap:8px}.ab-handt{margin:0;font-size:13px;font-weight:600;color:#071B35}'
    '.ab-fing{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}'
    '.ab-f{min-width:0;padding:10px 12px;border:1px solid #DCE3E9;border-radius:8px;display:flex;flex-direction:column;gap:4px}'
    '.ab-fn{font-size:12.5px;color:#4B5A6E;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
    '.ab-fv{font-size:20px;font-weight:600;line-height:1.2;font-variant-numeric:tabular-nums}'
    '.ab-fb{height:6px;background:#EEF2F5;border-radius:3px}.ab-fb>span{display:block;height:6px;border-radius:3px}'
    '.ab-fk{font-size:12px;color:#4B5A6E}'
    '.ab-cent{padding-top:12px}'
    '.ab-rk{display:grid;grid-template-columns:36px minmax(0,1fr) minmax(150px,auto);gap:12px;align-items:center;padding:10px 0;border-top:1px solid #EEF2F5}'
    '.ab-rkh{padding:6px 0;border-top:0;font-size:12px;color:#4B5A6E}.ab-rkn{color:#4B5A6E}'
    '.ab-rkc{display:flex;flex-direction:column;min-width:0}.ab-rkc>span:first-child{font-weight:500;color:#071B35}.ab-rkc>span:last-child{font-size:12px;color:#4B5A6E}'
    '.ab-rkm{display:flex;flex-direction:column;align-items:flex-end;text-align:right}.ab-rkm strong{font-weight:600;color:#071B35}.ab-rkm span{font-size:12px;color:#4B5A6E}'
    '@media (max-width:1240px){.ab-t7{gap:6px;font-size:13px}.ab-tr{padding-left:4px;padding-right:4px}.ab-f{padding:9px 9px}.ab-fv{font-size:18px}}'
    '@media (max-width:1100px){.ab-row2{grid-template-columns:minmax(0,1fr)}.ab-mods{grid-template-columns:repeat(2,minmax(0,1fr))}'
    '.ab-err{grid-template-columns:minmax(0,1fr)}.ab-errc{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-right:0;border-bottom:1px solid #E6EBF0}'
    '.ab-t7{gap:12px;font-size:inherit}.ab-f{padding:10px 12px}.ab-fv{font-size:20px}}'
    '@media (max-width:860px){.ab-errc{grid-template-columns:minmax(0,1fr);padding-left:20px;padding-right:20px}.ab-errt{padding-left:20px;padding-right:20px}}'
    '@media (max-width:760px){.ab-row3{grid-template-columns:minmax(0,1fr)}.ab-mods{grid-template-columns:minmax(0,1fr)}}'
    '@media (max-width:600px){.ab-fing{grid-template-columns:repeat(2,minmax(0,1fr))}.ab-hrow{grid-template-columns:76px minmax(0,1fr) 66px;gap:10px}'
    '.ab-rk{grid-template-columns:28px minmax(0,1fr) 116px}}'
)


def build():
    html = page('ABIS', 'Biometrie.dc.html', B.FILTERS, BODY, SCRIPT, 5130, '')
    for blk in (bandeau('Biometrie.dc.html'), filters(B.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + V3.CSS9 + EN.CSS_EN + CSS_AB + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
