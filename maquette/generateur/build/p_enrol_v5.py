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
swap("nf(cur.n - cur.rejN - cur.coursN) + ' NIU'", "nf(cur.n - Math.round(cur.rejN) - Math.round(cur.n * ECHP / 100) - Math.round(cur.coursN)) + ' NIU'")
swap("{ label: 'En cours', value: nf(132857), detail: '4,1 % des inscriptions' }",
     f"{{ label: 'En cours', value: nf({EC}), detail: '{pc(EC / INS * 100)} des inscriptions' }}")

# 4. pyramide âge et sexe : les barres portent le nombre de NIU (part de chaque tranche x NIU de la zone)
swap("const pyramid = bins.map((b) => ({ label: b[0], f: pct(b[1]), m: pct(b[2]), wf: (b[1] / 12.6 * 78).toFixed(1), wm: (b[2] / 12.6 * 78).toFixed(1) }));",
     "const zoneNiu = cur ? cur.n - Math.round(cur.rejN) - Math.round(cur.n * ECHP / 100) - Math.round(cur.coursN) : 3058886;\n"
     "    const cnt = [];\n"
     "    bins.forEach((b) => { cnt.push(Math.round(b[1] / 100 * zoneNiu)); cnt.push(Math.round(b[2] / 100 * zoneNiu)); });\n"
     "    const drift = Math.round(zoneNiu) - cnt.reduce((a, c) => a + c, 0);\n"
     "    cnt[6] += drift; // l'arrondi est absorbé par la plus grande tranche (femmes, 26 à 35 ans)\n"
     "    let totF = 0, totM = 0;\n"
     "    const pyramid = bins.map((b, i) => { totF += cnt[2 * i]; totM += cnt[2 * i + 1];\n"
     "      return { label: b[0], f: nf(cnt[2 * i]), m: nf(cnt[2 * i + 1]), wf: (b[1] / 12.6 * 70).toFixed(1), wm: (b[2] / 12.6 * 70).toFixed(1) }; });\n"
     "    const pyrF = nf(totF) + ' (' + pct(totF / (totF + totM) * 100) + ')', pyrM = nf(totM) + ' (' + pct(totM / (totF + totM) * 100) + ')';")
swap("      pyramid: pyramid,", "      pyramid: pyramid, pyrF: pyrF, pyrM: pyrM,")

# 5. tableau des zones : NIU générés et rejets en nombres, nouvelle colonne échoués (NIU + rejets + échoués + en cours = inscriptions)
#    les arrondis sont répartis pour que chaque colonne totalise exactement la zone (écart reporté sur la plus grande ligne)
swap("    src.sort((a, b) => b.n - a.n);\n",
     "    src.sort((a, b) => b.n - a.n);\n"
     "    const fix = (k, f) => { const v = src.map(f); const t = Math.round(v.reduce((a, c) => a + c, 0)); const r = v.map(Math.round);\n"
     "      r[0] += t - r.reduce((a, c) => a + c, 0); src.forEach((s, i) => { s[k] = r[i]; }); };\n"
     "    fix('rejI', (s) => s.n * s.rej / 100); fix('echI', (s) => s.n * ECHP / 100); fix('coursI', (s) => s.coursN);\n")
swap("niu: pct(100 - s.rej - s.cours - ECHP), rej: pct(s.rej),",
     "niu: nf(s.n - s.rejI - s.echI - s.coursI), rej: nf(s.rejI), ech: nf(s.echI), rejTip: 'Taux de rejet : ' + pct(s.rej),")
swap("cours: nf(s.coursN), delai:", "cours: nf(s.coursI), delai:")

# 6. top des centres : trois classements (plus d'enregistrements, plus d'échecs, plus de rejets), en nombres
_OLD_CSC = re.search(r"    const watch = \[.*?    const cscRows = tab === 'top' \? topList : watchList;\n", SCRIPT, re.S).group(0)
swap(_OLD_CSC, """    // centres fictifs (hors les 5 plus actifs, repris du BI actuel) : [nom, lieu, région, nombre, inscriptions du centre]
    const ech = [
      ['Centre n° 10247', 'Golfe, Grand Lomé', 'DAGL', 412, 21340],
      ['Centre n° 30118', 'Ogou, Plateaux', 'PLA', 286, 15870],
      ['Centre n° 60412', 'Kpendjal, Savanes', 'SAV', 241, 8230],
      ['Centre n° 20533', 'Bas-Mono, Maritime', 'MAR', 198, 7430],
      ['Centre n° 50318', 'Dankpen, Kara', 'KAR', 176, 7980],
      ['Centre n° 40105', 'Tchamba, Centrale', 'CEN', 152, 7800]
    ];
    const rej = [
      ['EPP Doumassesse I G/B', 'Golfe, Grand Lomé', 'DAGL', 871, 43534],
      ['Centre n° 60412', 'Kpendjal, Savanes', 'SAV', 790, 8230],
      ['Centre n° 60227', 'Oti, Savanes', 'SAV', 741, 8520],
      ['Centre n° 50318', 'Dankpen, Kara', 'KAR', 646, 7980],
      ['Centre n° 40105', 'Tchamba, Centrale', 'CEN', 601, 7800],
      ['Centre n° 20533', 'Bas-Mono, Maritime', 'MAR', 535, 7430]
    ];
    const inZone = (c) => !sel || c[2] === sel;
    const topList = top.filter(inZone).slice(0, 5).map((c, i) => ({ rank: String(i + 1), name: c[0], place: c[1], metric: nf(c[3]), sub: 'inscriptions' }));
    const rankOf = (list) => list.filter(inZone).slice(0, 5).map((c, i) => ({ rank: String(i + 1), name: c[0], place: c[1], metric: nf(c[3]),
      sub: pct(c[3] / c[4] * 100) + ' de ' + nf(c[4]) + ' inscriptions' }));
    const cscRows = tab === 'ech' ? rankOf(ech) : tab === 'rej' ? rankOf(rej) : topList;
""")
swap("tabTop: tabBtn('top'), tabWatch: tabBtn('watch'),", "tabTop: tabBtn('top'), tabEch: tabBtn('ech'), tabRej: tabBtn('rej'),")
swap("emptyText: tab === 'top' ? 'Aucun des centres les plus actifs du pays ne se trouve dans cette région.' : 'Aucun centre de cette région ne dépasse le seuil de rejet à surveiller.',",
     "emptyText: 'Aucun centre de ce classement ne se trouve dans cette région.',")
swap("metricLabel: tab === 'top' ? 'Inscriptions' : 'Taux de rejet'", "metricLabel: tab === 'ech' ? 'Échecs' : tab === 'rej' ? 'Rejets' : 'Inscriptions'")

# 7. en-tête du territoire : inscriptions et NIU générés de la zone choisie
swap("      pyramid: pyramid, pyrF: pyrF, pyrM: pyrM,",
     "      pyramid: pyramid, pyrF: pyrF, pyrM: pyrM,\n"
     "      zoneIns: nf(cur ? cur.n : NAT), zoneInsDetail: cur ? pct(cur.n / NAT * 100) + ' du total national' : 'dans 6 régions',\n"
     "      zoneNiu: nf(zoneNiu), zoneNiuPct: pct(zoneNiu / (cur ? cur.n : NAT) * 100),")

# 8. carte et liste des zones : taux de NIU (NIU générés / inscriptions) au lieu du taux de rejet ; plus foncé = meilleur taux
swap("classes: [[2.5, '#B7D3F6'], [3.0, '#6DA7EC'], [3.5, '#2A78D6'], [99, '#184F95']],",
     "classes: [[92, '#B7D3F6'], [93, '#6DA7EC'], [94, '#2A78D6'], [101, '#184F95']],")
swap("regionValue: (n) => round1(regByName[n].rej),", "regionValue: (n) => round1(100 - regByName[n].rej - regByName[n].cours - ECHP),")
swap("prefValue: (n) => prefIndex[n][2],", "prefValue: (n) => 100 - prefIndex[n][2] - prefIndex[n][3] - ECHP,")
swap("? n + ' : ' + pct(prefIndex[n][2]) + ' de rejets, ' + nf(prefIndex[n][1]) + ' inscriptions, délai médian ' + String(prefIndex[n][4]).replace('.', ',') + ' j'",
     "? n + ' : ' + pct(100 - prefIndex[n][2] - prefIndex[n][3] - ECHP) + ' de NIU générés, ' + nf(prefIndex[n][1]) + ' inscriptions, délai médian ' + String(prefIndex[n][4]).replace('.', ',') + ' j'")
swap(": n + ' : ' + pct(regByName[n].rej) + ' de rejets, ' + nf(regByName[n].n) + ' inscriptions',",
     ": n + ' : ' + pct(100 - regByName[n].rej - regByName[n].cours - ECHP) + ' de NIU générés, ' + nf(regByName[n].n) + ' inscriptions',")
swap("national: 'Togo : ' + pct(86496 / 3278239 * 100) + ' de rejets, ' + nf(3278239) + ' inscriptions',",
     "national: 'Togo : ' + pct(3058886 / 3278239 * 100) + ' de NIU générés, ' + nf(3278239) + ' inscriptions',")
swap("nationalValue: pct(86496 / 3278239 * 100)", "nationalValue: pct(3058886 / 3278239 * 100)")

# 3. cartes : une valeur par carte (pas de boucle, chaque carte a son icône)
swap("      map: map,\n      prereg: prereg,", "      map: map,\n      prereg: prereg,\n      pr0: prereg[0], pr1: prereg[1], pr2: prereg[2], pr3: prereg[3], pr4: prereg[4], pr5: prereg[5],\n      pt0: parts[0], pt1: parts[1], pt2: parts[2], pt3: parts[3],\n      fg0: figures[0], fg1: figures[1], fg2: figures[2], fg3: figures[3], fg4: figures[4],")

# =============== Bandeau : titre, fraîcheur, filtres ===============
def pill(label, options, min_w, values=None, attrs=''):
    vals = values or [None] * len(options)
    opts = ''.join(f'<option value="{v}">{o}</option>' if v is not None else f'<option>{o}</option>' for o, v in zip(options, vals))
    return f'<label class="v5-filter"><span>{label}</span><select {attrs}style="min-width: {min_w}px">{opts}</select></label>'


FRESH = ('<span class="v5-fresh"><svg width="13" height="13" viewBox="0 0 24 24" aria-hidden="true" '
         'style="fill: none; stroke: #071B35; stroke-width: 2.4; stroke-linecap: round"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>'
         'Dernière mise à jour : 14/01/2026 à 11h42</span>')
TITLE = ('<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 14px">\n'
         '<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px; align-self: stretch">'
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



# =============== Cartes : même design que les cartes de modules de la Vue d'ensemble (v9) ===============
_N, _G1, _G2 = '#013781', '#FFE7A3', '#FCBA21'
_IA = f'width="44" height="44" viewBox="0 0 48 48" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: {_N}; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round"'
_CAL = (f'<rect x="6" y="9" width="36" height="32" rx="4" fill="{_G1}"></rect><path d="M6 13a4 4 0 0 1 4-4h28a4 4 0 0 1 4 4v5H6z" fill="{_G2}"></path>'
        '<path d="M16 5v8M32 5v8"></path>')
IC = {
    'cal_ok': f'<svg {_IA}>{_CAL}<path d="m17 29 5 5 9-10" stroke-width="2.4"></path></svg>',
    'cal_x': f'<svg {_IA}>{_CAL}<path d="m19 25 10 10M29 25 19 35" stroke-width="2.4"></path></svg>',
    'wait': (f'<svg {_IA}><path d="M16 6c0 9 8 12 8 18s-8 9-8 18h16c0-9-8-12-8-18s8-9 8-18z" fill="{_G1}"></path>'
             f'<path d="M18.5 40c1.2-4.6 5.5-6.6 5.5-9 0 2.4 4.3 4.4 5.5 9z" fill="{_G2}" stroke="none"></path><path d="M13 6h22M13 42h22"></path></svg>'),
    'user_ok': (f'<svg {_IA}><circle cx="20" cy="15" r="6" fill="{_G2}"></circle><path d="M8 38c0-7 5.4-12 12-12s12 5 12 12z" fill="{_G1}"></path>'
                '<circle cx="35" cy="33" r="7.5" fill="#FFFFFF"></circle><path d="m31.5 33 2.5 2.5 5-5"></path></svg>'),
    'people': (f'<svg {_IA}><circle cx="31.5" cy="17" r="5" fill="{_G1}"></circle><path d="M24 37c.4-5.6 3.6-9.5 7.5-9.5S38.6 31.4 39 37z" fill="{_G1}"></path>'
               f'<circle cx="17" cy="15" r="6" fill="{_G2}"></circle><path d="M6 38c0-7 4.9-12 11-12s11 5 11 12z" fill="{_G2}"></path></svg>'),
    'clock': (f'<svg {_IA}><circle cx="24" cy="24" r="17" fill="{_G1}"></circle><path d="M24 7a17 17 0 0 0 0 34z" fill="{_G2}" stroke="none"></path>'
              '<circle cx="24" cy="24" r="17"></circle><path d="M24 14v10l7 4"></path></svg>'),
    'niu': (f'<svg {_IA}><rect x="5" y="10" width="38" height="28" rx="4" fill="{_G1}"></rect><path d="M5 14a4 4 0 0 1 4-4h5v28H9a4 4 0 0 1-4-4z" fill="{_G2}" stroke="none"></path>'
            '<rect x="5" y="10" width="38" height="28" rx="4"></rect><path d="m24 17-2 14M32 17l-2 14M19 21.5h16M18 26.5h16"></path></svg>'),
    'cours': (f'<svg {_IA}><circle cx="24" cy="24" r="17" fill="{_G1}" stroke="none"></circle><circle cx="24" cy="24" r="6" fill="{_G2}"></circle>'
              '<path d="M37 17.5A14.5 14.5 0 0 0 11.6 15M11 30.5A14.5 14.5 0 0 0 36.4 33M11 8.5v7h7M37 39.5v-7h-7"></path></svg>'),
    'echec': (f'<svg {_IA}><path d="M24 6 43 40H5z" fill="{_G1}"></path><path d="M24 6 5 40h19z" fill="{_G2}" stroke="none"></path>'
              '<path d="M24 6 43 40H5z"></path><path d="M24 18v11M24 34.5v.5" stroke-width="2.6"></path></svg>'),
    'rejet': (f'<svg {_IA}><circle cx="24" cy="24" r="17" fill="{_G1}"></circle><path d="M24 7a17 17 0 0 0 0 34z" fill="{_G2}" stroke="none"></path>'
              '<circle cx="24" cy="24" r="17"></circle><path d="m18 18 12 12M30 18 18 30" stroke-width="2.6"></path></svg>'),
    'delai': (f'<svg {_IA}><circle cx="24" cy="27" r="15" fill="{_G1}"></circle><path d="M24 12a15 15 0 0 0 0 30z" fill="{_G2}" stroke="none"></path>'
              '<circle cx="24" cy="27" r="15"></circle><path d="M20 5h8M24 5v7M24 20v7l5 3M37 13l2.5-2.5"></path></svg>'),
    'enrol': V3.ICONS9['enrol'].replace('width="52" height="52"', 'width="44" height="44"'),
}


def card(icon, var, chip=False, value_color=False, sub='detail'):
    """Carte au style v9 : icône bicolore à gauche ; à droite libellé (bleu ANID), valeur, détail. Les valeurs viennent du script ({{var.x}})."""
    ch = f'<i class="en-chip" style="background: {{{{{var}.color}}}}"></i>' if chip else ''
    vc = f' style="color: {{{{{var}.valueColor}}}}"' if value_color else ''
    return (f'<div class="v9-card en-card">{IC[icon]}<span class="v9-body"><span class="v9-name">{ch}{{{{{var}.label}}}}</span>'
            f'<span class="v9-val"{vc}>{{{{{var}.value}}}}</span><span class="v9-sub">{{{{{var}.{sub}}}}}</span></span></div>')

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
          '<div class="en-cards en-c3 en-pre-cards">'
          + card('cal_ok', 'pr0', value_color=True) + card('wait', 'pr1', value_color=True) + card('cal_x', 'pr2', value_color=True)
          + card('user_ok', 'pr3', value_color=True) + card('people', 'pr4', value_color=True) + card('clock', 'pr5', value_color=True)
          + '</div>\n</div>\n</section>\n')

# =============== 2. Devenir des inscriptions + semaines ===============
DEVENIR = ('<section aria-labelledby="devenir" class="v7-panel en-dev">\n' + BRACKETS + head('devenir', 'Devenir des inscriptions') +
           '<div class="v7-pbody en-devb">'
           f'<p class="en-big"><span class="en-bigv">{nf(NIU)}</span><span class="en-bigu">NIU générés, soit {pc(NIU / INS * 100)} des {nf(INS)} inscriptions</span></p>'
           f'<div role="img" aria-label="Devenir des inscriptions : NIU générés {pc(NIU / INS * 100)}, en cours {pc(EC / INS * 100)}, échoués {pc(ECH / INS * 100)}, rejetés {pc(REJ / INS * 100)}" class="en-split">\n'
           '<sc-for list="{{parts}}" as="p" hint-placeholder-count="4"><span title="{{p.tip}}" style="flex: {{p.w}} 1 0; background: {{p.color}}"></span></sc-for>\n</div>\n'
           '<div class="en-cards en-c2">'
           + card('niu', 'pt0', chip=True, sub='pct') + card('cours', 'pt1', chip=True, sub='pct')
           + card('echec', 'pt2', chip=True, sub='pct') + card('rejet', 'pt3', chip=True, sub='pct')
           + '</div>\n</div>\n</section>\n')

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
FIGS = ('<div class="en-cards en-c5 en-figcards" aria-label="Chiffres de la zone" role="group">'
        + card('enrol', 'fg0') + card('niu', 'fg1') + card('rejet', 'fg2') + card('cours', 'fg3') + card('delai', 'fg4') + '</div>\n')
MAPBLOCK = CM.block('map', 440, CM.legend('Taux de NIU générés', ['&lt; 92 %', '92 à 93 %', '93 à 94 %', '94 % et +']), brackets=False)
_CHEV = '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="fill: none; stroke: currentColor; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round"><polyline points="9 6 15 12 9 18"></polyline></svg>'
TABLE = ('<div class="v7-reg-tab">\n<p class="en-tt" id="souszones">{{tableTitle}}</p>\n'
         '<div role="table" aria-labelledby="souszones" class="en-table">\n'
         '<div role="row" class="en-tr en-th"><span role="columnheader">Zone</span><span role="columnheader">Inscriptions</span>'
         '<span role="columnheader">NIU générés</span><span role="columnheader">Rejets</span><span role="columnheader">Échoués</span><span role="columnheader">En cours</span><span role="columnheader">Délai médian</span></div>\n'
         '<sc-for list="{{rows}}" as="r" hint-placeholder-count="6">\n<div role="row" class="en-tr">\n<span role="rowheader">'
         '<sc-if value="{{r.canDrill}}" hint-placeholder-val="{{true}}"><button type="button" onClick="{{r.drill}}" class="en-drill">{{r.name}}' + _CHEV + '</button></sc-if>'
         '<sc-if value="{{r.cannotDrill}}" hint-placeholder-val="{{false}}"><span class="en-zn">{{r.name}}</span></sc-if></span>\n'
         '<span role="cell" title="{{r.tip}}">{{r.value}}</span><span role="cell">{{r.niu}}</span>'
         '<span role="cell" title="{{r.rejTip}}" style="font-weight: {{r.rejWeight}}"><sc-if value="{{r.high}}" hint-placeholder-val="{{false}}">'
         '<svg width="11" height="11" viewBox="0 0 24 24" aria-label="Taux élevé" style="margin-right: 4px; fill: #FAB219"><path d="M12 2 1 21h22L12 2z"></path></svg></sc-if>{{r.rej}}</span>'
         '<span role="cell">{{r.ech}}</span><span role="cell">{{r.cours}}</span><span role="cell">{{r.delai}}</span>\n</div>\n</sc-for>\n</div>\n</div>\n')
TERR = ('<section aria-labelledby="terr" class="v7-panel">\n'
        '<div class="v7-head"><div>' + _crumb + '<h2 id="terr" class="en-h2">{{zoneTitle}}</h2>'
        '<p class="en-sub">Carte colorée selon le taux de NIU : part des inscriptions qui ont leur NIU. Cliquez sur une région pour voir ses préfectures.</p></div>'
        '<dl class="en-zone" aria-label="Chiffres de la zone">'
        '<div><dt>Inscriptions</dt><dd class="en-zv">{{zoneIns}}</dd><dd class="en-zd">{{zoneInsDetail}}</dd></div>'
        '<div><dt>NIU générés</dt><dd class="en-zv">{{zoneNiu}}</dd><dd class="en-zd">{{zoneNiuPct}} des inscriptions</dd></div>'
        '</dl></div>\n'
        + '<div class="v7-pbody v7-reg">\n<div class="v7-reg-map">\n'  # 7 oct. : cartes de chiffres de la zone (FIGS) retirées à la demande
 + MAPBLOCK + '</div>\n' + TABLE + '</div>\n</section>\n')

# =============== 4. Âge et sexe, centres ===============
_pyr = re.search(r'(<div style="display: grid; grid-template-columns: minmax\(0, 1fr\) 72px minmax\(0, 1fr\); gap: 8px; font-size: 13px">.*?</sc-for>\n</div>\n)</section>', _old_body, re.S).group(1)
PYRAMIDE = ('<section aria-labelledby="pyramide" class="v7-panel">\n' + head('pyramide', 'NIU générés par âge et par sexe', '{{zoneLabel}}, nombre de NIU générés par tranche d’âge') +
            '<div class="v7-pbody en-pyr">\n' + _pyr.replace('Femmes, 53,0 %', 'Femmes : {{pyrF}}').replace('Hommes, 47,0 %', 'Hommes : {{pyrM}}')
            .replace('grid-template-columns: minmax(0, 1fr) 72px minmax(0, 1fr)', 'grid-template-columns: minmax(0, 1fr) 86px minmax(0, 1fr)') + '</div>\n</section>\n')
_csc = re.search(r'<section aria-labelledby="csc".*?</section>', _old_body, re.S).group(0)
_tabs = re.search(r'<div role="group" aria-label="Classement affiché".*?</div>', _csc, re.S).group(0)
_inner = _csc[_csc.index('<sc-if value="{{hasCsc}}"'):_csc.rindex('</section>')]
_btn = re.search(r'<button type="button" onClick="\{\{tabTop.pick\}\}".*?</button>', _tabs, re.S).group(0)
_btn = _btn.replace('padding: 0 14px', 'padding: 0 12px').replace('min-height: 40px', 'min-height: 36px')
TABS = ('<div role="group" aria-label="Classement affiché" class="en-tabs">'
        + _btn.replace('>Plus actifs<', '>Plus d’enregistrements<')
        + _btn.replace('tabTop.', 'tabEch.').replace('>Plus actifs<', '>Plus d’échecs<')
        + _btn.replace('tabTop.', 'tabRej.').replace('>Plus actifs<', '>Plus de rejets<') + '</div>')
assert TABS.count('<button') == 3 and 'Plus actifs' not in TABS
_inner = _inner.replace('grid-template-columns: 36px minmax(0, 1fr) 120px', 'grid-template-columns: 36px minmax(0, 1fr) minmax(120px, auto)')
assert _inner.count('minmax(120px, auto)') == 2
CENTRES = ('<section aria-labelledby="csc" class="v7-panel">\n' + head('csc', 'Top des centres', '{{zoneLabel}}', TABS) +
           '<div class="v7-pbody en-csc">\n' + _inner + '</div>\n</section>\n')
ROW4 = '<div class="en-row2 en-row4">\n' + PYRAMIDE + CENTRES + '</div>\n'

BODY = TITLE + PREREG + ROW2 + TERR + ROW4
for h in ('{{zoneIns}}', '{{zoneNiu}}', '{{pyrF}}', '{{pyrM}}', '{{pr0.value}}', '{{pt3.pct}}', '{{trend}}', '{{rows}}', '{{pyramid}}', '{{cscRows}}', '{{map.items}}', '{{zoneTitle}}', '{{goNational}}'):
    assert h in BODY, h

CSS_EN = (
    '.en-h2{margin:0;font-size:20px;font-weight:600;color:#071B35}.en-sub{margin:4px 0 0;font-size:13px;color:#4B5A6E}'
    '.en-big{margin:0;display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 12px}'
    '.en-bigv{font-size:38px;font-weight:600;letter-spacing:-0.025em;line-height:1.1;color:#071B35;font-variant-numeric:tabular-nums}'
    '.en-bigu{font-size:14px;color:#4B5A6E}'
    '.en-split{display:flex;gap:2px;height:10px;border-radius:5px;overflow:hidden}.en-split>span{min-width:3px}'
    '.en-leg{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:12.5px;color:#4B5A6E}'
    '.en-leg>span{display:inline-flex;align-items:center;gap:7px}.en-leg i{width:10px;height:10px;border-radius:2px}.en-leg strong{font-weight:600;color:#071B35}'
    '.en-cards{display:grid;gap:14px 16px}.en-c2{grid-template-columns:repeat(2,minmax(0,1fr))}'
    '.en-c3{grid-template-columns:repeat(3,minmax(0,1fr))}.en-c5{grid-template-columns:repeat(5,minmax(0,1fr))}'
    '.en-card{padding:16px 18px;gap:14px}.en-card:hover{border-color:#F5D77E;box-shadow:0 2px 6px rgba(7,27,53,.06)}'
    '.en-card .v9-name{display:inline-flex;align-items:center;gap:7px;font-size:13.5px;line-height:1.3}.en-card .v9-val{font-size:22px}'
    '.en-chip{flex-shrink:0;width:9px;height:9px;border-radius:2px}'
    '.en-pre-cards{padding:24px 28px 28px}.en-figcards{padding:22px 28px 6px}'
    '.en-pre{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.8fr)}'
    '.en-pre-main{padding:24px 28px 28px;display:flex;flex-direction:column;gap:14px;border-right:1px solid #E6EBF0}'
    '.en-facts{margin:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:#E6EBF0}'
    '.en-facts>div{background:#FFFFFF;padding:20px 24px;display:flex;flex-direction:column;gap:3px;min-width:0}'
    '.en-facts dt{font-size:12.5px;color:#4B5A6E}.en-fv{margin:0;font-size:22px;font-weight:600;letter-spacing:-0.01em;font-variant-numeric:tabular-nums}'
    '.en-fd{margin:0;font-size:12px;line-height:1.4;color:#4B5A6E}'
    '.en-row2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:24px;align-items:stretch}'
    '.en-row4{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}'
    '.en-dev{position:relative}.en-devb{display:flex;flex-direction:column;gap:18px;padding-bottom:42px}'
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
    '.en-zone{margin:0;display:flex;align-items:stretch;gap:0}'
    '.en-zone>div{display:flex;flex-direction:column;padding:0 24px;border-left:1px solid #E6EBF0}.en-zone>div:first-child{border-left:0;padding-left:0}.en-zone>div:last-child{padding-right:0}'
    '.en-zone dt{font-size:12.5px;color:#4B5A6E}.en-zv{margin:0;font-size:26px;font-weight:600;letter-spacing:-0.02em;line-height:1.2;color:#071B35;font-variant-numeric:tabular-nums;white-space:nowrap}'
    '.en-zd{margin:0;font-size:12px;color:#4B5A6E}'
    '.en-tt{margin:0 0 6px;font-size:15px;font-weight:600;color:#071B35}'
    '.en-table{min-width:480px;font-variant-numeric:tabular-nums}'
    '.en-tr{display:grid;grid-template-columns:minmax(116px,1.35fr) repeat(6,minmax(58px,1fr));gap:12px;align-items:center;padding:0 8px;border-top:1px solid #EEF2F5}'
    '.en-tr>span:not(:first-child){text-align:right}'
    '.en-th{align-items:end;padding-top:6px;padding-bottom:8px;border-top:0;font-size:12px;line-height:1.35;color:#4B5A6E}'
    '.en-drill{display:inline-flex;align-items:center;gap:4px;min-height:42px;white-space:nowrap;padding:0;border:0;background:transparent;font-family:inherit;font-size:14px;font-weight:600;color:#013781;cursor:pointer;text-align:left}'
    '.en-drill:hover{color:#071B35}.en-zn{display:inline-flex;align-items:center;min-height:42px;font-weight:500}'
    '.en-tabs{display:flex;flex-wrap:wrap;gap:2px;padding:3px;border-radius:8px;background:#F1F4F6}.en-tabs button{white-space:nowrap}'
    '.en-pyr{display:flex;flex-direction:column;gap:14px}.en-csc{display:flex;flex-direction:column;gap:6px;padding-top:12px}'
    '@media (max-width:1240px){.en-tr{grid-template-columns:minmax(92px,1.2fr) repeat(6,minmax(56px,1fr));gap:6px;padding:0 4px;font-size:13px}.en-th{font-size:11.5px}.en-c5{grid-template-columns:repeat(3,minmax(0,1fr))}}'
    '@media (max-width:1340px){.en-card{padding:14px 14px;gap:12px}.en-card>svg{width:38px;height:38px}}'
    '@media (max-width:1100px){.en-pre,.en-row2{grid-template-columns:minmax(0,1fr)}.en-pre-main{border-right:0;border-bottom:1px solid #E6EBF0}'
    '}'
    '@media (max-width:1000px){.en-tr{gap:12px;font-size:inherit}}'
    '@media (max-width:860px){.en-c3,.en-c5{grid-template-columns:repeat(2,minmax(0,1fr))}}'
    '@media (max-width:600px){.en-zv{font-size:22px}.en-zone>div{padding:0 16px}.en-csc [role=row]{grid-template-columns:28px minmax(0,1fr) 116px !important}.en-csc [role=row]>span:last-child{text-align:right}.en-c2,.en-c3,.en-c5{grid-template-columns:minmax(0,1fr)}.en-pre-main{padding:16px 20px}'
    '.en-pre-cards,.en-figcards{padding:16px 20px}.en-bigv{font-size:32px}}'
)


def build():
    html = page('Enrôlement', 'Enrolement.dc.html', p_enrol.FILTERS, BODY, SCRIPT, 2600, '')
    for blk in (bandeau('Enrolement.dc.html'), filters(p_enrol.FILTERS)):
        assert html.count(blk) == 1
        html = html.replace(blk, '')
    html = html.replace('\n</style>\n</helmet>', '\n' + V3.CSS + V3.CSS7 + V3.CSS9 + CSS_EN + '\n</style>\n</helmet>', 1)
    old = ('<div class="bande-bio" aria-hidden="true" style="height: 230px"></div>\n<main style="position: relative; max-width: 1376px; '
           'margin: -230px auto 0; padding: 40px 32px 56px;')
    assert html.count(old) == 1
    html = html.replace(old, old.replace('230px', '220px').replace('padding: 40px', 'padding: 30px'))
    return html
