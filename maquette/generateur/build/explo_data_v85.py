"""Cube de données de l'Exploration (8 oct. 2026).

Marges reprises des autres pages (régions de l'Enrôlement et de l'Impression des cartes, pyramide des NIU,
types de demande, types et causes d'authentification, erreurs IDPS) ; le reste est réparti selon des profils
de test. Chaque tableau croisé est arrondi de façon contrôlée : ses lignes et ses colonnes redonnent
exactement les marges, et toutes les marges redonnent le total de l'indicateur.
"""
import itertools

# ---------------- dimensions ----------------
REG = ['Grand Lomé', 'Plateaux', 'Maritime', 'Savanes', 'Kara', 'Centrale']
SEX = ['Femmes', 'Hommes']
AGE = ['0 à 5 ans', '6 à 14 ans', '15 à 18 ans', '19 à 25 ans', '26 à 35 ans', '36 à 45 ans', '46 à 60 ans', '60 ans et +']
TYPE = ['Nouvelle inscription', 'Mise à jour', 'Mise à jour par le citoyen', 'Correction', 'Réimpression de carte',
        'Récupération de NIU', 'Activation', 'Désactivation']
MO = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']


def months(y0, m0, y1, m1):
    out, y, m = [], y0, m0
    while (y, m) <= (y1, m1):
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def lr(total, weights):
    """Plus grand reste : entiers proportionnels aux poids, de somme exacte."""
    s = sum(weights)
    raw = [total * w / s for w in weights]
    out = [int(x) for x in raw]
    rest = total - sum(out)
    for i in sorted(range(len(raw)), key=lambda i: -(raw[i] - out[i]))[:rest]:
        out[i] += 1
    return out


def cross(rows, cols, base=None):
    """Tableau entier de marges exactes (lignes = rows, colonnes = cols), proche de base (sinon indépendance)."""
    T = sum(rows)
    assert T == sum(cols), (T, sum(cols))
    if T == 0:
        return [[0] * len(cols) for _ in rows]
    raw = [[(base[i][j] if base else r * c / T) for j, c in enumerate(cols)] for i, r in enumerate(rows)]
    if base:  # recalage proportionnel itératif sur les marges
        for _ in range(60):
            for i, r in enumerate(rows):
                s = sum(raw[i]) or 1
                raw[i] = [x * r / s for x in raw[i]]
            for j, c in enumerate(cols):
                s = sum(raw[i][j] for i in range(len(rows))) or 1
                for i in range(len(rows)):
                    raw[i][j] *= c / s
    x = [lr(r, raw[i]) if r else [0] * len(cols) for i, r in enumerate(rows)]
    for _ in range(10000):
        d = [cols[j] - sum(x[i][j] for i in range(len(rows))) for j in range(len(cols))]
        up = [j for j in range(len(cols)) if d[j] > 0]
        dn = [j for j in range(len(cols)) if d[j] < 0]
        if not up:
            break
        j, k = up[0], dn[0]
        cand = [i for i in range(len(rows)) if x[i][k] > 0]
        i = max(cand, key=lambda i: (raw[i][j] - x[i][j]) - (raw[i][k] - x[i][k]))
        x[i][k] -= 1
        x[i][j] += 1
    for i, r in enumerate(rows):
        assert sum(x[i]) == r
    for j, c in enumerate(cols):
        assert sum(x[i][j] for i in range(len(rows))) == c
    return x


# ---------------- profils ----------------
ENR_M = months(2024, 1, 2026, 1)          # janv. 2024 à janv. 2026 (du 1er au 14)
_enr_w = [40, 70, 95, 110, 120, 125, 128, 130, 132, 134, 136, 138,          # 2024
          140, 142, 144, 146, 148, 150, 151, 152, 150, 132, 150, 146,       # 2025
          35]                                                              # janv. 2026, du 1er au 14
CAR_M = months(2024, 2, 2026, 1)          # impression : un mois après l'inscription
_car_w = _enr_w[:23] + [52]
AUT_M = months(2025, 2, 2026, 1)          # authentification : depuis février 2025
_aut_w = [28, 34, 42, 48, 52, 55, 57, 58, 47, 51, 43, 14]
IDPS_M = [(2026, 7)]

PYR_F = [33648, 131532, 116238, 287535, 385420, 284476, 256946, 125414]   # pyramide des NIU (Enrôlement)
PYR_M = [36707, 140709, 113179, 256946, 339536, 247770, 220240, 82590]
NIU = 3058886
assert sum(PYR_F) + sum(PYR_M) == NIU
SEX_W = [sum(PYR_F), sum(PYR_M)]
AGE_W = [f + m for f, m in zip(PYR_F, PYR_M)]

# régions (tableaux des pages Enrôlement et Impression des cartes)
R_INS = [1020000, 598000, 512000, 450239, 386000, 312000]
R_NIU = [961808, 556639, 479495, 413573, 358514, 288857]
R_REJ = [20917, 16541, 12381, 16072, 11069, 9516]
R_ECH = [2868, 1682, 1440, 1266, 1085, 877]
R_ENC = [34407, 23138, 18684, 19328, 15332, 12750]
R_EXP = [975000, 563000, 486000, 423590, 362000, 292000]
R_REM = [690000, 300000, 268000, 188796, 176000, 148000]
assert sum(R_INS) == 3278239 and sum(R_NIU) == NIU and sum(R_REJ) == 86496 and sum(R_ECH) == 9218 and sum(R_ENC) == 123639
assert sum(R_EXP) == 3101590 and sum(R_REM) == 1770796
TYPE_INS = [3249758, 12689, 6214, 3905, 2870, 2051, 640, 112]
assert sum(TYPE_INS) == 3278239


def mlabel(y, m):
    return f'{MO[m - 1]} {y}'


DIMS = {
    'region': {'label': 'Région', 'sort': 'value'},
    'annee': {'label': 'Année', 'sort': 'natural'},
    'mois': {'label': 'Mois', 'sort': 'natural', 'rowsOnly': True},
    'sexe': {'label': 'Sexe', 'sort': 'natural'},
    'age': {'label': 'Tranche d’âge', 'sort': 'natural'},
    'type': {'label': 'Type de demande', 'sort': 'value'},
    'taut': {'label': 'Type d’authentification', 'sort': 'value'},
    'cause': {'label': 'Cause d’échec', 'sort': 'value'},
    'part': {'label': 'Partenaire', 'sort': 'value'},
    'terr': {'label': 'Type d’erreur', 'sort': 'value'},
}


def measure(key, label, total, marg, base_pairs=None):
    """marg : {dim: (valeurs, marges)} ; mois → année dérivée automatiquement."""
    marg = dict(marg)
    if 'mois' in marg:
        mv, mm = marg['mois']
        years = sorted({y for y, _ in mv})
        marg['annee'] = ([str(y) for y in years], [sum(n for (y, _), n in zip(mv, mm) if y == yy) for yy in years])
        marg['mois'] = ([mlabel(y, m) for y, m in mv], mm)
    for d, (vals, ns) in marg.items():
        assert sum(ns) == total, (key, d, sum(ns), total)
        assert len(vals) == len(ns)
    dims = [d for d in DIMS if d in marg]
    pairs = {}
    for a, b in itertools.combinations(dims, 2):
        if {a, b} == {'mois', 'annee'}:
            continue
        if b == 'mois':
            a, b = b, a
        if 'annee' in (a, b) and 'mois' in marg:
            continue  # dérivé plus bas depuis le croisement avec le mois
        base = (base_pairs or {}).get((a, b))
        pairs[f'{a}|{b}'] = cross(marg[a][1], marg[b][1], base)
    if 'mois' in marg:
        mv = marg['mois'][0]
        ys = marg['annee'][0]
        for b in dims:
            if b in ('mois', 'annee'):
                continue
            mx = pairs[f'mois|{b}']
            pairs[f'annee|{b}'] = [[sum(mx[i][j] for i, lab in enumerate(mv) if lab.endswith(y)) for j in range(len(mx[0]))] for y in ys]
    return {'key': key, 'label': label, 'total': total, 'dims': dims,
            'marg': {d: marg[d][1] for d in dims}, 'vals': {d: marg[d][0] for d in dims}, 'pairs': pairs}


def enr(key, label, total, regs, with_type=False, pyr=None):
    marg = {'region': (REG, regs), 'mois': (ENR_M, lr(total, _enr_w)), 'sexe': (SEX, pyr[0] if pyr else lr(total, SEX_W)),
            'age': (AGE, pyr[1] if pyr else lr(total, AGE_W))}
    if with_type:
        marg['type'] = (TYPE, TYPE_INS)
    base = {('sexe', 'age'): [PYR_F, PYR_M]}
    return measure(key, label, total, marg, base)


def car(key, label, total, regs):
    return measure(key, label, total, {'region': (REG, regs), 'mois': (CAR_M, lr(total, _car_w)),
                                       'sexe': (SEX, lr(total, SEX_W)), 'age': (AGE, lr(total, AGE_W))},
                   {('sexe', 'age'): [PYR_F, PYR_M]})


def abis(key, label, total):
    return measure(key, label, total, {'mois': (ENR_M, lr(total, _enr_w))})


SOURCES = [
    {'key': 'enrol', 'label': 'Enrôlement', 'note': '', 'measures': [
        enr('ins', 'Inscriptions', 3278239, R_INS, with_type=True),
        enr('niu', 'NIU générés', NIU, R_NIU, pyr=([sum(PYR_F), sum(PYR_M)], AGE_W)),
        enr('enc', 'Inscriptions en cours', 123639, R_ENC),
        enr('ech', 'Inscriptions échouées', 9218, R_ECH),
        enr('rej', 'Inscriptions rejetées', 86496, R_REJ)]},
    {'key': 'cartes', 'label': 'Impression des cartes', 'note': '', 'measures': [
        car('dem', 'Demandes d’impression', 3113431, lr(3113431, R_EXP)),
        car('exp', 'Cartes imprimées et expédiées', 3101590, R_EXP),
        car('rem', 'Cartes remises', 1770796, R_REM),
        car('arem', 'Cartes à remettre', 1330794, [e - r for e, r in zip(R_EXP, R_REM)])]},
    {'key': 'abis', 'label': 'ABIS', 'note': 'Les journaux ABIS ne contiennent ni région ni profil du citoyen : seules les ventilations par date sont disponibles.', 'measures': [
        abis('ins', 'Requêtes d’insertion', 3159591), abis('dedup', 'Requêtes de déduplication', 3158734),
        abis('adj', 'Requêtes d’adjudication', 41870), abis('trt', 'Cas d’adjudication traités', 39205),
        abis('hit', 'Dossiers HIT', 16002), abis('nohit', 'Dossiers NO HIT', 23203),
        abis('eins', 'Erreurs d’insertion', 857), abis('eid', 'Erreurs d’identification', 1104), abis('eadj', 'Erreurs d’adjudication', 312)]},
    {'key': 'idps', 'label': 'IDPS', 'note': 'Les 14 ordres d’impression IDPS datent tous du 3 juillet 2026 et viennent tous des Savanes.', 'measures': [
        measure('ord', 'Ordres d’impression reçus', 14, {'region': (REG, [0, 0, 0, 14, 0, 0]), 'mois': (IDPS_M, [14])}),
        measure('att', 'Ordres en attente', 14, {'region': (REG, [0, 0, 0, 14, 0, 0]), 'mois': (IDPS_M, [14])}),
        measure('err', 'Erreurs d’impression', 14, {'region': (REG, [0, 0, 0, 14, 0, 0]), 'mois': (IDPS_M, [14]),
                                                    'terr': (['Personnalisation', 'Contrôle qualité', 'Supervision'], [3, 5, 6])})]},
    {'key': 'auth', 'label': 'Authentifications', 'note': 'Les requêtes d’authentification ne portent pas la région du demandeur.', 'measures': [
        measure('req', 'Requêtes', 510499, {'mois': (AUT_M, lr(510499, _aut_w)),
                                            'taut': (['Biométrique', 'Code à usage unique', 'Démographique', 'Combinée'], [490080, 18380, 1290, 749]),
                                            'part': (['Atos'], [510499])}),
        measure('ok', 'Requêtes réussies', 215736, {'mois': (AUT_M, lr(215736, [w * (0.44 if i < 8 else 0.41) for i, w in enumerate(_aut_w)])),
                                                    'taut': (['Biométrique', 'Code à usage unique', 'Démographique', 'Combinée'], [199780, 14520, 900, 536]),
                                                    'part': (['Atos'], [215736])}),
        measure('ko', 'Requêtes échouées', 294763, {'mois': (AUT_M, lr(294763, [w * (0.56 if i < 8 else 0.59) for i, w in enumerate(_aut_w)])),
                                                    'taut': (['Biométrique', 'Code à usage unique', 'Démographique', 'Combinée'], [290300, 3860, 390, 213]),
                                                    'cause': (['Empreinte non concordante', 'Qualité de capture insuffisante', 'NIU ou identifiant virtuel invalide ou inactif',
                                                               'Code OTP expiré ou erroné', 'Autres causes'], [168400, 71200, 29800, 3860, 21503]),
                                                    'part': (['Atos'], [294763])})]},
]
# cohérences avec les autres pages
_auth = {m['key']: m for m in SOURCES[4]['measures']}
assert [a + b for a, b in zip(_auth['ok']['marg']['taut'], _auth['ko']['marg']['taut'])] == _auth['req']['marg']['taut']
_e = {m['key']: m for m in SOURCES[0]['measures']}
assert _e['niu']['pairs']['sexe|age'] == [PYR_F, PYR_M]
N_MEASURES = sum(len(s['measures']) for s in SOURCES)


def cube():
    return {'dims': DIMS, 'sources': SOURCES}


if __name__ == '__main__':
    import json
    js = json.dumps(cube(), ensure_ascii=False, separators=(',', ':'))
    print(N_MEASURES, 'indicateurs', len(js), 'octets')
    print(_e['ins']['pairs']['region|sexe'])
    print(_e['ins']['marg']['annee'], _e['ins']['vals']['annee'])
