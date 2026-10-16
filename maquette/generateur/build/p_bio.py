"""Onglet ABIS (v4.2) : tous les KPI ABIS illustrés avec des DONNÉES DE TEST.

Aucune valeur des captures du BI actuel ni du document IN Groupe v0.2 n'est reprise.
Scénario de test aligné sur le reste de la maquette : activité de déc. 2024 au 14/01/2026 (arrêt de l'alimentation).
Cohérences voulues :
- recherches de doublons 3 158 734 = 96,4 % des 3 278 239 inscriptions ;
- recherches sans insertion 20 743 = HIT 16 002 + adjudication en attente 2 353 + erreurs d'identification 1 104 + sans réponse 1 284 ;
- HIT 16 002 = rejets pour doublon de l'onglet Qualité et technique ;
- adjudication : reçus 41 870 = traités 39 205 + en attente 2 353 + en erreur 312 ; traités = HIT 16 002 + NO HIT 23 203.
"""
from common import *
import p_bio_v41 as OLD

FILTERS = OLD.FILTERS
NAVY, MUTED = '#071B35', '#4B5A6E'
I_WARN, I_INFO, ICONS, ARROW = OLD.I_WARN, OLD.I_INFO, OLD.ICONS, OLD.ARROW
LEVEL_COLORS = {'Faible': '#B7D3F6', 'Moyen': '#6DA7EC', 'Excellent': '#184F95'}
C_DEDUP, C_INS = '#013781', '#6DA7EC'
C_HIT, C_NOHIT, C_ERR, C_WAIT = '#D03B3B', '#2A78D6', '#EC835A', '#FAB219'


def nf(n):
    return f'{n:,}'.replace(',', ' ')


def dec(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',').replace('-', '−')


def pct(x, d=1):
    return dec(x, d) + ' %'


# ====================== Données de test ======================
INSCRIPTIONS = 3278239
DEDUP, INSERT = 3158734, 3137991
ERR_ID, ERR_INS, ERR_ADJ = 1104, 857, 312
SANS_REPONSE, SANS_REPONSE_24H = 1284, 212
ADJ_RECUS, ADJ_TRAITES, ADJ_ATTENTE = 41870, 39205, 2353
HIT, NOHIT = 16002, 23203
ADJ_ATTENTE_7J = 640
assert DEDUP - INSERT == HIT + ADJ_ATTENTE + ERR_ID + SANS_REPONSE
assert ADJ_RECUS == ADJ_TRAITES + ADJ_ATTENTE + ERR_ADJ and ADJ_TRAITES == HIT + NOHIT

# Requêtes par mois (déc. 2024 à janv. 2026 ; janvier 2026 du 1er au 14)
MOIS = ['déc.', 'janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.', 'janv.']
ANNEES = {0: '2024', 1: '2025', 13: '2026'}
_raw = [95, 160, 190, 230, 255, 270, 262, 258, 249, 266, 281, 274, 239, 129]
_k = DEDUP / sum(_raw)
M_DEDUP = [round(v * _k) for v in _raw]
M_DEDUP[-2] += DEDUP - sum(M_DEDUP)
M_INS = [round(v * INSERT / DEDUP) for v in M_DEDUP]
M_INS[-2] += INSERT - sum(M_INS)

# Jours de la semaine (part des recherches de doublons)
JOURS = [('Lun', 'lundi', 18.9), ('Mar', 'mardi', 19.4), ('Mer', 'mercredi', 19.1), ('Jeu', 'jeudi', 18.7),
         ('Ven', 'vendredi', 16.2), ('Sam', 'samedi', 6.1), ('Dim', 'dimanche', 1.6)]

# Détail par jour : jour, recherches, insertions, erreurs, délai médian (s)
DAYS = [('Mercredi 14/01/2026', 4812, 4779, 2, 39), ('Mardi 13/01/2026', 12406, 12331, 4, 44), ('Lundi 12/01/2026', 12118, 12040, 3, 42),
        ('Dimanche 11/01/2026', 1037, 1031, 0, 31), ('Samedi 10/01/2026', 3902, 3879, 1, 35), ('Vendredi 09/01/2026', 10655, 10590, 5, 47),
        ('Jeudi 08/01/2026', 11874, 11806, 3, 43)]

# Erreurs par cause : (cause, insertion, déduplication, adjudication)
CAUSES = [('Données biométriques inaccessibles', 402, 518, 96), ('Erreur interne de l’ABIS', 211, 287, 41),
          ('Format biométrique invalide', 76, 214, 46), ('Référence introuvable', 0, 85, 129), ('Référence déjà présente', 168, 0, 0)]
assert sum(c[1] for c in CAUSES) == ERR_INS and sum(c[2] for c in CAUSES) == ERR_ID and sum(c[3] for c in CAUSES) == ERR_ADJ

# Adjudication par semaine (12 semaines complètes) : HIT, NO HIT, erreurs, en attente en fin de semaine
SEMAINES = ['20/10', '27/10', '03/11', '10/11', '17/11', '24/11', '01/12', '08/12', '15/12', '22/12', '29/12', '05/01']
W_HIT = [298, 312, 305, 321, 334, 318, 341, 352, 329, 287, 214, 336]
W_NOHIT = [436, 451, 447, 463, 470, 459, 488, 502, 471, 418, 305, 481]
W_ERR = [5, 6, 4, 7, 5, 6, 8, 6, 5, 4, 3, 6]
W_WAIT = [1712, 1748, 1801, 1836, 1874, 1902, 1958, 2011, 2067, 2148, 2301, 2290]

# Adjudication par région : code, nom, part des dossiers reçus, en attente, erreurs, taux de HIT, délai médian (jours)
_REG = [('DAGL', 'Grand Lomé', 0.29, 562, 84, 0.38, 2.1), ('PLA', 'Plateaux', 0.18, 398, 55, 0.40, 2.5), ('MAR', 'Maritime', 0.16, 341, 48, 0.41, 2.4),
        ('SAV', 'Savanes', 0.15, 489, 51, 0.46, 3.8), ('KAR', 'Kara', 0.12, 315, 41, 0.42, 3.2), ('CEN', 'Centrale', 0.10, 248, 33, 0.39, 2.9)]
REGIONS = []
for code, name, share, wait, err, hr, d in _REG:
    recus = round(ADJ_RECUS * share)
    REGIONS.append([name, recus, wait, err, recus - wait - err, hr, d])
REGIONS[-1][1] += ADJ_RECUS - sum(r[1] for r in REGIONS)
REGIONS[-1][4] = REGIONS[-1][1] - REGIONS[-1][2] - REGIONS[-1][3]
assert sum(r[2] for r in REGIONS) == ADJ_ATTENTE and sum(r[3] for r in REGIONS) == ERR_ADJ and sum(r[4] for r in REGIONS) == ADJ_TRAITES
for r in REGIONS:
    r.append(round(r[4] * r[5]))
REGIONS[0][7] += HIT - sum(r[7] for r in REGIONS)
assert sum(r[7] for r in REGIONS) == HIT

# Agents d'adjudication (pseudonymisés) : dossiers traités, taux de HIT, délai médian (jours)
AGENTS = [['Agent 01', 6214, 0.398, 1.9], ['Agent 02', 5902, 0.412, 2.2], ['Agent 03', 5488, 0.439, 2.4], ['Agent 04', 5130, 0.386, 2.6],
          ['Agent 05', 4876, 0.401, 2.8], ['Agent 06', 4402, 0.473, 3.1], ['Agent 07', 3951, 0.369, 3.4], ['Agent 08', 3242, 0.415, 4.2]]
assert sum(a[1] for a in AGENTS) == ADJ_TRAITES
for a in AGENTS:
    a.append(round(a[1] * a[2]))
AGENTS[0][4] += HIT - sum(a[4] for a in AGENTS)
assert sum(a[4] for a in AGENTS) == HIT

# Qualité : niveaux (%), score moyen, min, max, échelle, tranches (%)
Q_FINGER = dict(levels=[3, 12, 85], score=99.8, smin=14, smax=236, scale=255, bins=[3, 10, 33, 35, 14, 3.5, 1, 0.5])
Q_IRIS = dict(levels=[1, 6, 93], score=80.3, smin=27, smax=99, scale=100, bins=[0, 0.3, 0.4, 0.6, 1.2, 2.5, 8, 28, 42, 17])
Q_FACE = dict(levels=[1, 3, 96], score=212.3, smin=71, smax=255, scale=255, bins=[0.3, 0.4, 0.8, 1.5, 3.5, 10, 40, 43.5])
EYES = [('Œil gauche', 80.9), ('Œil droit', 79.7)]
DOIGTS = {'Main droite': [('Pouce', 121, 44), ('Index', 108, 46), ('Majeur', 112, 41), ('Annulaire', 97, 43), ('Auriculaire', 71, 27)],
          'Main gauche': [('Pouce', 118, 42), ('Index', 104, 45), ('Majeur', 101, 39), ('Annulaire', 92, 40), ('Auriculaire', 74, 26)]}
assert round(sum(v for h in DOIGTS.values() for _, v, _ in h) / 10, 1) == Q_FINGER['score']
NBPK = round(sum(n for h in DOIGTS.values() for _, _, n in h) / 10, 1)
DOIGTS_NON_CAPTURES = 0.9


# ====================== Composants ======================
def tile(label, value, detail, extra=''):
    return (f'<div style="background: #FFFFFF; padding: 16px 18px; display: flex; flex-direction: column; gap: 4px">'
            f'<span style="font-size: 13px; color: {MUTED}">{label}</span><span style="font-size: 24px; font-weight: 600">{value}</span>{extra}'
            f'<span style="font-size: 12px; color: {MUTED}">{detail}</span></div>')


def legend(items):
    return ('<span style="display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 12px; color: #4B5A6E">'
            + ''.join(f'<span style="display: inline-flex; align-items: center; gap: 6px"><span style="width: 10px; height: 10px; border-radius: 2px; background: {c}"></span>{l}</span>' for l, c in items)
            + '</span>')


def table(label, cols, header, rows, min_w, total=None):
    """cols : grille CSS ; header : [(texte, align)] ; rows : listes de cellules HTML (la première est l'en-tête de ligne)."""
    def row(cells, style='', head=False):
        out = f'<div role="row" style="display: grid; grid-template-columns: {cols}; gap: 14px; align-items: center; {style}">'
        for i, (c, (_, al)) in enumerate(zip(cells, header)):
            role = 'columnheader' if head else ('rowheader' if i == 0 else 'cell')
            out += f'<span role="{role}" style="text-align: {al}">{c}</span>'
        return out + '</div>\n'
    h = row([t for t, _ in header], 'padding: 6px 0; font-size: 12px; color: #4B5A6E', head=True)
    body = ''.join(row(r, 'padding: 9px 0; border-top: 1px solid #EEF2F5') for r in rows)
    tot = row(total, 'padding: 9px 0; border-top: 1px solid #C5CFDA; font-weight: 600') if total else ''
    return (f'<div style="overflow-x: auto"><div role="table" aria-label="{label}" style="min-width: {min_w}px; font-variant-numeric: tabular-nums">\n'
            + h + body + tot + '</div></div>\n')


def bar_cell(v, vmax, color, text, w_text=64, weight='400'):
    return (f'<span style="display: flex; align-items: center; gap: 10px"><span style="flex-grow: 1; height: 10px; background: #E3EAF3; border-radius: 0 4px 4px 0">'
            f'<span style="display: block; height: 10px; width: {v / vmax * 100:.1f}%; background: {color}; border-radius: 0 4px 4px 0"></span></span>'
            f'<span style="width: {w_text}px; text-align: right; font-weight: {weight}">{text}</span></span>')


def section(sid, title_, sub, body, extra_head='', gap=16):
    return (f'<section aria-labelledby="{sid}" style="{CARD}; display: flex; flex-direction: column; gap: {gap}px">\n'
            f'<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 8px 24px">\n'
            f'<div><h2 id="{sid}" style="{H2}">{title_}</h2>' + (f'<p style="{SUB}">{sub}</p>' if sub else '') + f'</div>\n{extra_head}</div>\n{body}</section>\n')


# ====================== 1. Transactions ABIS ======================
_mmax = 300000
_bars = []
for i, (m, d, s) in enumerate(zip(MOIS, M_DEDUP, M_INS)):
    partial = i == len(MOIS) - 1
    op = '0.55' if partial else '1'
    _bars.append(f'<div title="{m} {ANNEES.get(i, "2025" if i < 13 else "2026")}{" (du 1er au 14)" if partial else ""} : {nf(d)} recherches, {nf(s)} insertions" '
                 f'style="flex: 1 1 0; display: flex; align-items: flex-end; justify-content: center; gap: 2px; height: 120px; opacity: {op}">'
                 f'<span style="width: 38%; height: {d / _mmax * 120:.1f}px; background: {C_DEDUP}; border-radius: 2px 2px 0 0"></span>'
                 f'<span style="width: 38%; height: {s / _mmax * 120:.1f}px; background: {C_INS}; border-radius: 2px 2px 0 0"></span></div>')
GRID = ''.join(f'<span aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: {v / _mmax * 120:.1f}px; border-top: 1px solid #EEF2F5"></span>'
               f'<span aria-hidden="true" style="position: absolute; left: 0; bottom: {v / _mmax * 120 + 2:.1f}px; font-size: 11px; color: {MUTED}">{nf(v)}</span>'
               for v in (100000, 200000, 300000))
MONTHLY = (f'<div style="flex: 3 1 560px; min-width: 0; display: flex; flex-direction: column; gap: 8px">'
           f'<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px 24px; font-size: 13px">'
           f'<span style="font-weight: 500">Requêtes ABIS par mois</span>' + legend([('Recherches de doublons', C_DEDUP), ('Insertions', C_INS)]) + '</div>'
           '<div style="overflow-x: auto"><div style="min-width: 560px">'
           f'<div role="img" aria-label="Requêtes ABIS par mois, de décembre 2024 à janvier 2026 : de {nf(M_DEDUP[0])} recherches en décembre 2024 à un pic de {nf(max(M_DEDUP))} en octobre 2025 ; janvier 2026 couvre du 1er au 14." '
           f'style="position: relative; display: flex; gap: 6px; padding-left: 52px; padding-top: 16px; border-bottom: 1px solid #9AA7B5">' + GRID + ''.join(_bars) + '</div>'
           '<div aria-hidden="true" style="display: flex; gap: 6px; padding-left: 52px; padding-top: 4px; font-size: 12px; color: #4B5A6E">'
           + ''.join(f'<span style="flex: 1 1 0; text-align: center; line-height: 1.3">{m}' + (f'<br><strong style="font-weight: 600; color: #071B35">{ANNEES[i]}</strong>' if i in ANNEES else '') + '</span>'
                     for i, m in enumerate(MOIS))
           + '</div></div></div><span style="font-size: 12px; color: #4B5A6E">Janvier 2026 : du 1er au 14.</span></div>')

_wmax = 20
WEEKDAYS = ('<div style="flex: 1 1 260px; min-width: 0; display: flex; flex-direction: column; gap: 8px">'
            '<span style="font-size: 13px; font-weight: 500">Recherches par jour de la semaine</span>'
            '<div role="img" aria-label="Part des recherches de doublons par jour de la semaine : ' + ', '.join(f'{l} {pct(p)}' for _, l, p in JOURS) + '" '
            'style="display: flex; gap: 8px; align-items: flex-end; height: 140px; border-bottom: 1px solid #9AA7B5">'
            + ''.join(f'<div style="flex: 1 1 0; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 4px; height: 140px">'
                      f'<span style="font-size: 11.5px; color: {MUTED}; white-space: nowrap">{dec(p)}</span>'
                      f'<span style="width: 70%; height: {p / _wmax * 112:.1f}px; background: {C_DEDUP}; border-radius: 2px 2px 0 0"></span></div>' for _, _, p in JOURS)
            + '</div><div aria-hidden="true" style="display: flex; gap: 8px; font-size: 12px; color: #4B5A6E">'
            + ''.join(f'<span style="flex: 1 1 0; text-align: center">{c}</span>' for c, *_ in JOURS)
            + '</div><span style="font-size: 12px; color: #4B5A6E">En % des recherches de doublons.</span></div>')

TILES = (tile('Inscriptions passées par l’ABIS', pct(DEDUP / INSCRIPTIONS * 100), f'{nf(DEDUP)} sur {nf(INSCRIPTIONS)} inscriptions',
              f'<span aria-hidden="true" style="height: 6px; background: #EEF2F5; border-radius: 3px"><span style="display: block; width: {DEDUP / INSCRIPTIONS * 100:.1f}%; height: 6px; background: {C_DEDUP}; border-radius: 3px"></span></span>')
         + tile('Recherches sans insertion', nf(DEDUP - INSERT), 'Doublons, dossiers en adjudication, en erreur ou sans réponse')
         + tile('Envoyées en adjudication', pct(ADJ_RECUS / DEDUP * 100), f'{nf(ADJ_RECUS)} ressemblances signalées')
         + tile('Délai médian de déduplication', '41 s', '90 % en moins de 3 min 12 s ; insertion : 3 s')
         + tile('Taux d’erreur ABIS', pct((ERR_ID + ERR_INS) / (DEDUP + INSERT) * 100, 2), f'{nf(ERR_ID + ERR_INS)} erreurs sur {nf(DEDUP + INSERT)} requêtes')
         + tile('Requêtes sans réponse', nf(SANS_REPONSE), f'Dont {nf(SANS_REPONSE_24H)} depuis plus de 24 heures'))

ABIS = ('<section aria-labelledby="abis" style="position: relative; background: #FFFFFF; border-radius: 8px; padding: 36px 40px; box-sizing: border-box; display: flex; flex-direction: column; gap: 28px">\n'
        + BRACKETS
        + '<div style="display: flex; flex-wrap: wrap; gap: 24px 48px; align-items: flex-start">\n'
          '<div style="flex: 1 1 300px; display: flex; flex-direction: column; gap: 6px">\n'
          '<h2 id="abis" style="margin: 0; font-size: 15px; font-weight: 500; color: #4B5A6E">Recherches de doublons dans l’ABIS</h2>\n'
          f'<span style="font-size: clamp(40px, 9vw, 56px); font-weight: 600; letter-spacing: -0.02em; line-height: 1.05">{nf(DEDUP)}</span>\n'
          f'<p style="margin: 4px 0 0; font-size: 15px">{nf(INSERT)} dossiers insérés dans la base biométrique.</p>\n'
          '<div style="display: flex; flex-direction: column; gap: 4px; margin-top: 8px; font-size: 13px; color: #4B5A6E">'
          f'<span style="display: inline-flex; align-items: center; gap: 6px">{I_INFO}{nf(ERR_ID)} erreurs d’identification</span>'
          f'<span style="display: inline-flex; align-items: center; gap: 6px">{I_INFO}{nf(ERR_INS)} erreurs d’insertion</span></div>\n'
          '</div>\n'
          '<div style="flex: 2 1 600px; min-width: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr)); gap: 1px; background: #E6EBEF; border: 1px solid #E6EBEF; border-radius: 6px; overflow: hidden">\n'
        + TILES + '\n</div>\n</div>\n'
        + '<div style="display: flex; flex-wrap: wrap; gap: 24px 40px; align-items: flex-start">\n' + MONTHLY + WEEKDAYS + '\n</div>\n</section>\n')

# ====================== 2. Détail par jour ======================
_c8 = 'minmax(170px, 1.3fr) repeat(6, minmax(92px, 1fr))'
_h8 = [('Jour', 'left'), ('Recherches de doublons', 'right'), ('Insertions', 'right'), ('Sans insertion', 'right'), ('Erreurs', 'right'), ('Taux d’erreur', 'right'), ('Délai médian', 'right')]
_r8 = [[d, nf(a), nf(b), nf(a - b), nf(e), pct(e / (a + b) * 100, 2), f'{s} s'] for d, a, b, e, s in DAYS]
_ta, _tb, _te = sum(d[1] for d in DAYS), sum(d[2] for d in DAYS), sum(d[3] for d in DAYS)
DETAIL = section('detail-jour', 'Détail des requêtes par jour', 'Sept derniers jours, toutes les zones.',
                 table('Requêtes ABIS par jour', _c8, _h8, _r8, 820, ['Total, 7 jours', nf(_ta), nf(_tb), nf(_ta - _tb), nf(_te), pct(_te / (_ta + _tb) * 100, 2), '42 s']), gap=10)

# ====================== 3. Erreurs par type et par cause ======================
_svc = [('Insertion', ERR_INS, INSERT), ('Déduplication', ERR_ID, DEDUP), ('Adjudication', ERR_ADJ, ADJ_RECUS)]
ERR_TILES = ('<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(200px, 100%), 1fr)); gap: 1px; background: #E6EBEF; border: 1px solid #E6EBEF; border-radius: 6px; overflow: hidden">'
             + ''.join(tile(f'Erreurs d’{s.lower()}' if s[0] in 'AEIOU' else f'Erreurs de {s.lower()}', nf(n), f'{pct(n / base * 100, 2)} des ' + ('dossiers reçus' if s == 'Adjudication' else 'requêtes')) for s, n, base in _svc) + '</div>')
_cmax = max(c[1] + c[2] + c[3] for c in CAUSES)
_c3 = 'minmax(220px, 1.6fr) repeat(3, minmax(90px, 0.7fr)) minmax(200px, 1.4fr)'
_h3 = [('Cause', 'left'), ('Insertion', 'right'), ('Déduplication', 'right'), ('Adjudication', 'right'), ('Total', 'left')]
_r3 = [[c, nf(a), nf(b), nf(d), bar_cell(a + b + d, _cmax, C_ERR, nf(a + b + d))] for c, a, b, d in sorted(CAUSES, key=lambda c: -(c[1] + c[2] + c[3]))]
ERREURS = section('erreurs', 'Erreurs ABIS par type et par cause', 'Réponses en erreur renvoyées par l’ABIS à MOSIP.',
                  ERR_TILES + table('Erreurs ABIS par cause', _c3, _h3, _r3, 760,
                                    ['Total', nf(ERR_INS), nf(ERR_ID), nf(ERR_ADJ), f'<span style="display: block; text-align: right">{nf(ERR_INS + ERR_ID + ERR_ADJ)}</span>']))


# ====================== 4. Adjudication ======================
def step(label, value, sub='', stacked=False, accent=None):
    border = f'border-left: 4px solid {accent}; ' if accent else ''
    return (f'<div style="flex: {"0 0 auto" if stacked else "1 1 160px"}; min-width: 0; border: 1px solid #DCE3E9; {border}border-radius: 6px; padding: 12px 14px; display: flex; flex-direction: column; gap: 2px; background: #F7F9FB">'
            f'<span style="font-size: 12.5px; color: {MUTED}">{label}</span><span style="font-size: 22px; font-weight: 600">{value}</span>'
            + (f'<span style="font-size: 12px; color: {MUTED}">{sub}</span>' if sub else '') + '</div>')


FLOW = ('<div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: stretch">'
        + step('Dossiers reçus', nf(ADJ_RECUS), f'{pct(ADJ_RECUS / DEDUP * 100)} des recherches de doublons') + ARROW
        + step('Dossiers traités', nf(ADJ_TRAITES), f'Taux de traitement {pct(ADJ_TRAITES / (ADJ_TRAITES + ADJ_ATTENTE) * 100)}') + ARROW
        + '<div style="flex: 1 1 200px; min-width: 0; display: flex; flex-direction: column; gap: 6px">'
        + step('HIT : doublon confirmé', nf(HIT), f'{pct(HIT / ADJ_TRAITES * 100)} des dossiers traités', True, C_HIT)
        + step('NO HIT : pas de doublon', nf(NOHIT), f'{pct(NOHIT / ADJ_TRAITES * 100)} des dossiers traités', True, C_NOHIT) + '</div></div>')

ADJ_KPI = ('<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(200px, 100%), 1fr)); gap: 12px 24px; padding-top: 14px; border-top: 1px solid #EEF2F5">'
           f'<div style="display: flex; gap: 10px; align-items: flex-start; padding: 12px 14px; border-radius: 6px; background: #FFF5DA">{I_WARN}'
           f'<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 13px; color: #6B4A00">En attente d’un agent</span><span style="font-size: 20px; font-weight: 600">{nf(ADJ_ATTENTE)}</span>'
           f'<span style="font-size: 12px; color: #6B4A00">Dont {nf(ADJ_ATTENTE_7J)} depuis plus de 7 jours</span></div></div>'
           f'<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 13px; color: {MUTED}">Dossiers en erreur</span><span style="font-size: 20px; font-weight: 600">{nf(ERR_ADJ)}</span>'
           f'<span style="font-size: 12px; color: {MUTED}">{pct(ERR_ADJ / ADJ_RECUS * 100, 2)} des dossiers reçus</span></div>'
           f'<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 13px; color: {MUTED}">Délai médian de décision</span><span style="font-size: 20px; font-weight: 600">2,6 jours</span>'
           f'<span style="font-size: 12px; color: {MUTED}">90 % en moins de 9 jours</span></div>'
           f'<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 13px; color: {MUTED}">Candidats examinés</span><span style="font-size: 20px; font-weight: 600">1,7</span>'
           f'<span style="font-size: 12px; color: {MUTED}">par dossier, en moyenne</span></div></div>')

_amax = 1000
_wq = max(W_WAIT)
AJ8 = ('<div style="flex: 1 1 460px; min-width: 0; display: flex; flex-direction: column; gap: 8px">'
       '<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 4px 16px; font-size: 13px">'
       '<span style="font-weight: 500">Décisions par semaine</span>' + legend([('HIT', C_HIT), ('NO HIT', C_NOHIT), ('Erreurs', C_ERR)]) + '</div>'
       '<div role="img" aria-label="Décisions d’adjudication par semaine, du 20/10/2025 au 05/01/2026 : ' + ', '.join(f'{s} {h + n} décisions dont {h} HIT' for s, h, n in zip(SEMAINES, W_HIT, W_NOHIT)) + '" '
       'style="display: flex; gap: 6px; align-items: flex-end; height: 110px; border-bottom: 1px solid #9AA7B5">'
       + ''.join(f'<div title="Semaine du {s} : {h} HIT, {n} NO HIT, {e} erreurs" style="flex: 1 1 0; display: flex; flex-direction: column; justify-content: flex-end; height: 110px">'
                 f'<span style="height: {e / _amax * 110:.1f}px; min-height: 2px; background: {C_ERR}; border-radius: 2px 2px 0 0"></span>'
                 f'<span style="height: {n / _amax * 110:.1f}px; background: {C_NOHIT}; border-top: 1px solid #FFFFFF"></span>'
                 f'<span style="height: {h / _amax * 110:.1f}px; background: {C_HIT}; border-top: 1px solid #FFFFFF"></span></div>'
                 for s, h, n, e in zip(SEMAINES, W_HIT, W_NOHIT, W_ERR))
       + '</div>'
       f'<div style="display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-top: 8px; font-size: 13px"><span style="font-weight: 500">En attente en fin de semaine</span>{legend([("En attente", C_WAIT)])}</div>'
       '<div role="img" aria-label="Dossiers en attente en fin de semaine : de ' + nf(W_WAIT[0]) + ' le 20/10 à ' + nf(W_WAIT[-1]) + ' le 05/01" style="display: flex; gap: 6px; align-items: flex-end; height: 48px; border-bottom: 1px solid #9AA7B5">'
       + ''.join(f'<span title="Semaine du {s} : {nf(w)} dossiers en attente" style="flex: 1 1 0; height: {w / _wq * 48:.1f}px; background: {C_WAIT}; border-radius: 2px 2px 0 0"></span>' for s, w in zip(SEMAINES, W_WAIT))
       + '</div><div aria-hidden="true" style="display: flex; gap: 6px; font-size: 11.5px; color: #4B5A6E">'
       + ''.join(f'<span style="flex: 1 1 0; text-align: center">{s if i % 2 == 0 else ""}</span>' for i, s in enumerate(SEMAINES)) + '</div></div>')

_c9 = 'minmax(110px, 1.3fr) repeat(5, minmax(64px, 0.8fr)) minmax(70px, 0.8fr)'
_h9 = [('Région', 'left'), ('Reçus', 'right'), ('En attente', 'right'), ('HIT', 'right'), ('NO HIT', 'right'), ('Erreurs', 'right'), ('Délai médian', 'right')]
_r9 = [[r[0], nf(r[1]), nf(r[2]), nf(r[7]), nf(r[4] - r[7]), nf(r[3]), f'{dec(r[6])} j']
       for r in sorted(REGIONS, key=lambda r: -r[1])]
AJ9 = ('<div style="flex: 1 1 520px; min-width: 0; display: flex; flex-direction: column; gap: 4px">'
       '<span style="font-size: 13px; font-weight: 500">Dossiers par région</span>'
       + table('Dossiers d’adjudication par région', _c9, _h9, _r9, 560,
               ['Togo', nf(ADJ_RECUS), nf(ADJ_ATTENTE), nf(HIT), nf(NOHIT), nf(ERR_ADJ), '2,6 j']) + '</div>')

ADJ = section('adjudication', 'Adjudication des doublons', 'Un agent tranche quand l’ABIS signale une ressemblance.',
              FLOW + ADJ_KPI + '<div style="display: flex; flex-wrap: wrap; gap: 24px 40px; padding-top: 16px; border-top: 1px solid #EEF2F5">' + AJ8 + AJ9 + '</div>', gap=18)

# ====================== 5. Agents d'adjudication ======================
_amax2 = max(a[1] for a in AGENTS)
_c10 = 'minmax(100px, 0.8fr) minmax(220px, 2fr) repeat(3, minmax(90px, 0.8fr))'
_h10 = [('Agent', 'left'), ('Dossiers traités', 'left'), ('HIT', 'right'), ('Part de HIT', 'right'), ('Délai médian', 'right')]
_avg_hit = HIT / ADJ_TRAITES
_r10 = [[a[0], bar_cell(a[1], _amax2, C_DEDUP, nf(a[1])), nf(a[4]),
         (f'<span style="display: inline-flex; align-items: center; gap: 4px; font-weight: 600"><svg width="12" height="12" viewBox="0 0 24 24" role="img" aria-label="Écart de plus de 5 points à la moyenne" style="fill: #FAB219"><path d="M12 2 1 21h22L12 2z"></path></svg>{pct(a[4] / a[1] * 100)}</span>'
          if abs(a[4] / a[1] - _avg_hit) > 0.05 else pct(a[4] / a[1] * 100)), f'{dec(a[3])} j'] for a in AGENTS]
AGENTS_SEC = section('agents', 'Activité des agents d’adjudication', 'Agents pseudonymisés. Part de HIT moyenne : ' + pct(_avg_hit * 100) + '.',
                     table('Activité des agents d’adjudication', _c10, _h10, _r10, 640,
                           ['Total', f'<span style="display: block; text-align: right; padding-right: 0">{nf(ADJ_TRAITES)}</span>', nf(HIT), pct(_avg_hit * 100), '2,6 j']), gap=10)


# ====================== 6. Qualité des captures ======================
def hist(q, name):
    bins = q['bins']
    n = len(bins)
    top = max(bins)
    step_ = q['scale'] / n
    bars = ''.join(f'<span title="{round(i * step_)} à {round((i + 1) * step_)} : {dec(v)} % des captures" style="flex: 1 1 0; height: {max(v / top * 48, 2 if v else 0.5):.1f}px; '
                   f'background: {"#013781" if v else "#DCE3E9"}; border-radius: 2px 2px 0 0"></span>' for i, v in enumerate(bins))
    mean_x = q['score'] / q['scale'] * 100
    return (f'<div style="display: flex; flex-direction: column; gap: 4px">'
            f'<span style="font-size: 13px; color: {MUTED}">Répartition des scores</span>'
            f'<div role="img" aria-label="{name} : répartition des scores de 0 à {q["scale"]}, moyenne {dec(q["score"])}" style="position: relative; display: flex; gap: 2px; align-items: flex-end; height: 48px; border-bottom: 1px solid #9AA7B5">{bars}'
            f'<span aria-hidden="true" style="position: absolute; left: calc({mean_x:.1f}% - 1px); top: -4px; bottom: 0; width: 2px; background: #071B35"></span></div>'
            '<div aria-hidden="true" style="display: flex; justify-content: space-between; font-size: 11.5px; color: #4B5A6E">'
            f'<span>0</span><span>{q["scale"] // 2}</span><span>{q["scale"]}</span></div></div>')


def modality(icon, name, q, extra=''):
    labs = ['Faible', 'Moyen', 'Excellent']
    seg = ''.join(f'<div title="{l} : {v} %" style="width: {v}%; background: {LEVEL_COLORS[l]}"></div>' for l, v in zip(labs, q['levels']) if v)
    leg = ''.join(f'<span style="display: inline-flex; align-items: center; gap: 5px"><span style="width: 9px; height: 9px; border-radius: 2px; background: {LEVEL_COLORS[l]}"></span>{l}&nbsp;{v}&nbsp;%</span>'
                  for l, v in zip(labs, q['levels']) if v)
    return f'''<div style="flex: 1 1 300px; min-width: 0; border: 1px solid #DCE3E9; border-radius: 8px; padding: 20px 22px; display: flex; flex-direction: column; gap: 12px">
<div style="display: flex; align-items: center; gap: 10px">{ICONS[icon]}<h3 style="margin: 0; font-size: 16px; font-weight: 600">{name}</h3></div>
<div style="display: flex; align-items: baseline; gap: 8px"><span style="font-size: 32px; font-weight: 600; letter-spacing: -0.01em">{q['levels'][2]}&nbsp;%</span><span style="font-size: 13px; color: #4B5A6E">de captures excellentes</span></div>
<div role="img" aria-label="{name} : {', '.join(f'{l} {v} %' for l, v in zip(labs, q['levels']) if v)}" style="display: flex; gap: 2px; height: 12px; border-radius: 3px; overflow: hidden">{seg}</div>
<div style="display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 12px; color: #4B5A6E">{leg}</div>
<div style="padding-top: 12px; border-top: 1px solid #EEF2F5; display: flex; flex-direction: column; gap: 8px">
<div style="display: flex; justify-content: space-between; align-items: baseline; gap: 12px"><span style="font-size: 13px; color: #4B5A6E">Score moyen</span><strong style="font-size: 16px; font-weight: 600">{dec(q['score'])}</strong></div>
{hist(q, name)}
<div style="display: flex; justify-content: space-between; font-size: 12px; color: #4B5A6E; font-variant-numeric: tabular-nums"><span>min {q['smin']}</span><span>max {q['smax']}</span></div>
{extra}
</div>
</div>'''


def kv(label, value):
    return (f'<div style="display: flex; justify-content: space-between; align-items: baseline; gap: 12px"><span style="font-size: 13px; color: #4B5A6E">{label}</span>'
            f'<strong style="font-size: 15px; font-weight: 600">{value}</strong></div>')


FINGER_EXTRA = kv('Indice NBPK moyen', dec(NBPK)) + kv('Doigts non capturés', pct(DOIGTS_NON_CAPTURES))
IRIS_EXTRA = ''.join(kv(l, dec(v)) for l, v in EYES)


def finger_color(v):
    return '#184F95' if v >= 110 else '#2A78D6' if v >= 95 else '#6DA7EC' if v >= 80 else '#B7D3F6'


DOIGTS_HTML = ('<div style="display: flex; flex-direction: column; gap: 10px; padding-top: 18px; border-top: 1px solid #EEF2F5">'
               '<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 4px 16px; align-items: baseline">'
               '<h3 style="margin: 0; font-size: 16px; font-weight: 600">Empreintes : qualité par doigt</h3>'
               + legend([('110 et plus', '#184F95'), ('95 à 110', '#2A78D6'), ('80 à 95', '#6DA7EC'), ('Moins de 80', '#B7D3F6')]) + '</div>'
               + ''.join('<div style="display: flex; flex-direction: column; gap: 6px"><span style="font-size: 13px; color: #4B5A6E">' + main + '</span>'
                         '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(150px, 100%), 1fr)); gap: 8px">'
                         + ''.join(f'<div style="border: 1px solid #DCE3E9; border-radius: 6px; padding: 10px 12px; display: flex; flex-direction: column; gap: 4px">'
                                   f'<span style="display: flex; justify-content: space-between; align-items: center; gap: 6px; font-size: 12.5px; color: #4B5A6E">{d}'
                                   + (f'<svg width="12" height="12" viewBox="0 0 24 24" role="img" aria-label="Score faible" style="flex-shrink: 0; fill: #FAB219"><path d="M12 2 1 21h22L12 2z"></path></svg>' if v < 80 else '')
                                   + f'</span><span style="font-size: 20px; font-weight: 600">{v}</span>'
                                   f'<span aria-hidden="true" style="height: 6px; background: #EEF2F5; border-radius: 3px"><span style="display: block; width: {v / 255 * 100:.1f}%; height: 6px; background: {finger_color(v)}; border-radius: 3px"></span></span>'
                                   f'<span style="font-size: 12px; color: #4B5A6E">NBPK {nb}</span></div>' for d, v, nb in doigts)
                         + '</div></div>' for main, doigts in DOIGTS.items())
               + '</div>')

QUALITY = section('qualite', 'Qualité des captures biométriques', 'Niveaux de qualité, score moyen et répartition des scores. Le trait marque la moyenne.',
                  '<div style="display: flex; flex-wrap: wrap; gap: 16px">'
                  + modality('finger', 'Empreintes digitales', Q_FINGER, FINGER_EXTRA)
                  + modality('iris', 'Iris', Q_IRIS, IRIS_EXTRA)
                  + modality('face', 'Visage', Q_FACE) + '</div>' + DOIGTS_HTML,
                  '<span style="font-size: 13px; color: #4B5A6E">Dernière capture le 14/01/2026 à 11h37</span>')

CENTRES = OLD.CENTRES
TITLE = ('<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px 16px">\n'
         '<h1 style="margin: 0; font-size: 28px; font-weight: 600; letter-spacing: -0.01em; color: #FFFFFF">ABIS : déduplication, adjudication et qualité</h1>\n'
         '<span style="display: inline-flex; align-items: center; min-height: 28px; padding: 2px 12px; box-sizing: border-box; border-radius: 14px; background: #FCBA21; color: #071B35; font-size: 13px; font-weight: 600">Données de test</span>\n</div>\n')
BODY = TITLE + ABIS + DETAIL + ERREURS + ADJ + AGENTS_SEC + QUALITY + CENTRES
_OLD_C = OLD.SCRIPT[OLD.SCRIPT.index('    const C = ['):OLD.SCRIPT.index('    const idx =')]
_NEW_C = '''    const C = [
      ['Centre n° 60412', 'Kpendjal, Savanes', 4210, [71.4, 6.8], [84.1, 3.1], [89.6, 2.9]],
      ['Centre n° 60227', 'Oti, Savanes', 3480, [74.9, 5.9], [86.5, 2.4], [91.8, 2.2]],
      ['Centre n° 50318', 'Dankpen, Kara', 2960, [77.2, 5.1], [88.2, 1.9], [93.1, 1.8]],
      ['Centre n° 60188', 'Tône, Savanes', 12404, [79.5, 4.6], [90.4, 1.3], [94.2, 1.4]],
      ['Centre n° 40233', 'Haho, Plateaux', 10109, [81.3, 4.1], [91.6, 1.1], [95.0, 1.1]],
      ['Centre n° 30145', 'Zio, Maritime', 15971, [82.6, 3.7], [92.8, 0.9], [95.6, 0.9]]
    ];
'''
SCRIPT = OLD.SCRIPT.replace(_OLD_C, _NEW_C)
assert 'Centre n° 30145' in SCRIPT
FOOTER = ''


def build():
    return page('ABIS', 'Biometrie.dc.html', FILTERS, BODY, SCRIPT, 4790, FOOTER)
