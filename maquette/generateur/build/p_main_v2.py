"""Vue d'ensemble retenue le 2 oct. 2026 (ex-version 2) : p_main.py modifié par sept changements.

Le bandeau de fraîcheur (1) est commun à tous les onglets depuis la v4 (common.bandeau).

1. Bandeau de fraîcheur explicite sous l'en-tête.
2. Titre de section « De la pré-inscription à la remise de la carte » et sous-titre chiffré.
3. Flux : « Demandes non imprimées » et « Cartes encore à remettre ».
4. Alertes en deux groupes, au format sévérité, problème, impact, action.
5. Tuile « Taux de remise » à la place de « Authentifications réussies ».
6. Tableau régional : colonne « Écart à la moyenne » et seuil de vigilance à 50 %.
7. Bloc compact « Qualité des données ».
"""
import re
from common import *
import journey_flow as JF
import p_main

NAME = 'MainV2.dc.html'
BODY = p_main.BODY
SCRIPT = p_main.SCRIPT


def swap(text, old, new, count=1):
    assert text.count(old) == count, (old[:80], text.count(old))
    return text.replace(old, new)


# ---------- 2 et 3 : en-tête de section et flux ----------
BODY = swap(BODY, 'Du rendez-vous à la carte en main', 'De la pré-inscription à la remise de la carte')
BODY = swap(BODY, 'Sur 3 278 239 inscrits, 1 770 796 ont reçu leur carte.',
            '3 278 239 inscrits, 1 770 796 cartes remises, soit <strong style="font-weight: 600">54,0 %</strong>.')
BODY = swap(BODY, JF.svg_simple(), JF.svg_simple(v2=True))
# v4.4 : frise à chevrons à la place du flux
BODY = swap(BODY, '<div class="parcours-flux" style="overflow-x: auto"><div style="min-width: 820px">' + JF.svg_simple(v2=True) + '</div></div>\n', JF.timeline_html())

# ---------- 4, 5 et 7 : alertes, tuiles, qualité ----------
ALERTES = '''<section aria-labelledby="traiter" style="flex: 1 1 520px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 22px">
<h2 id="traiter" style="''' + H2 + '''">À traiter</h2>
''' + ''.join('''<div>
<h3 style="margin: 0 0 6px; display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: #4B5A6E">%s<span style="min-width: 22px; height: 22px; padding: 0 6px; box-sizing: border-box; border-radius: 11px; background: #E3EAF3; color: #013781; display: inline-flex; align-items: center; justify-content: center; font-size: 12px">%d</span></h3>
<ul style="list-style: none; margin: 0; padding: 0">
<sc-for list="{{%s}}" as="a" hint-placeholder-count="%d">
<li class="alerte">
<div style="display: flex; flex-direction: column; align-items: flex-start; gap: 4px">
<span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 8px; border-radius: 4px; background: {{a.bg}}; color: {{a.fg}}; font-size: 12px; font-weight: 600; white-space: nowrap"><svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true" style="fill: {{a.color}}; stroke: none"><path d="M12 2 1 21h22L12 2z"></path></svg>{{a.level}}</span>
<span style="font-size: 12px; color: #4B5A6E">{{a.module}}</span>
</div>
<div style="display: flex; flex-direction: column; gap: 3px; min-width: 0">
<span style="font-size: 15px; font-weight: 600; line-height: 1.35">{{a.title}}</span>
<span style="font-size: 13px; color: #4B5A6E"><span style="font-weight: 600; color: #071B35">Impact :</span> {{a.impact}}</span>
</div>
<a href="{{a.href}}" class="alerte-action">{{a.cta}}</a>
</li>
</sc-for>
</ul>
</div>
''' % (t, n, var, n) for t, n, var in [('Actions requises', 4, 'actions'), ('À surveiller', 2, 'watch')]) + '''</section>'''

ICO_X = '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: #D03B3B"><circle cx="12" cy="12" r="11"></circle><path d="M8 8l8 8M16 8l-8 8" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round"></path></svg>'
ICO_W = '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: #FAB219"><path d="M12 2 1 21h22L12 2z"></path></svg>'
ICO_OK = '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: #2E9E63"><circle cx="12" cy="12" r="11"></circle><path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"></path></svg>'


def qrow(label, note, value):
    return ('<li class="qrow"><div style="display: flex; flex-direction: column; gap: 2px; min-width: 0">'
            '<span style="font-size: 14px; font-weight: 500">%s</span><span style="font-size: 12px; color: #4B5A6E">%s</span></div>%s</li>\n' % (label, note, value))


QUALITE = ('''<section aria-labelledby="qualite" style="''' + CARD + '''; display: flex; flex-direction: column; gap: 6px">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 4px 16px">
<h2 id="qualite" style="''' + H2 + '''">Qualité des données</h2>
<a href="Technique.dc.html" style="display: inline-flex; align-items: center; min-height: 44px; font-size: 13px; font-weight: 600">Voir les contrôles</a>
</div>
<ul style="list-style: none; margin: 0; padding: 0">
''' + qrow('Fraîcheur des données', 'Dernière alimentation le 14/01/2026',
            '<span style="display: inline-flex; align-items: center; gap: 6px; font-size: 18px; font-weight: 600; color: #8A1F1F; white-space: nowrap"><svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="fill: none; stroke: #D03B3B; stroke-width: 2.4; stroke-linecap: round"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>261 jours</span>')
    + qrow('Contrôles de cohérence', '7 règles vérifiées à chaque chargement',
           '<span style="display: flex; flex-direction: column; gap: 2px; font-size: 13px">'
           '<span style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap">' + ICO_X + '<strong style="font-weight: 600">3</strong> non conformes</span>'
           '<span style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap">' + ICO_W + '<strong style="font-weight: 600">2</strong> à vérifier</span>'
           '<span style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap">' + ICO_OK + '<strong style="font-weight: 600">2</strong> conformes</span></span>')
    + qrow('Compteurs faux dans le BI actuel', 'Synchronisés négatifs, pré-inscriptions réservées à zéro, plus de cartes que de NIU',
           '<span style="font-size: 18px; font-weight: 600">3</span>')
    + '</ul>\n</section>')

_alerts_old = re.search(r'<section aria-labelledby="traiter".*?</section>', BODY, re.S).group(0)
BODY = swap(BODY, _alerts_old, ALERTES)
_tiles_old = re.search(r'<section aria-label="Indicateurs clés".*?</section>', BODY, re.S).group(0)
_tiles_new = _tiles_old.replace('flex: 1 1 440px; min-width: 0; ', '')
BODY = swap(BODY, _tiles_old, '<div style="flex: 1 1 440px; min-width: 0; display: flex; flex-direction: column; gap: 24px">\n'
            + _tiles_new + '\n' + QUALITE + '\n</div>')

_old_alerts_js = SCRIPT[SCRIPT.index('    const alerts = ['):SCRIPT.index('    const tiles = [')]
_new_alerts_js = r'''    const SEV = {
      'Critique': { color: '#D03B3B', bg: '#FCEBEB', fg: '#6E1414' },
      'Priorité élevée': { color: '#EC835A', bg: '#FDEEE7', fg: '#7A3413' },
      'À surveiller': { color: '#FAB219', bg: '#FEF4DC', fg: '#664700' }
    };
    const al = (level, module, title, impact, cta, href) => Object.assign({ level: level, module: module, title: title, impact: impact, cta: cta, href: href }, SEV[level]);
    const actions = [
      al('Critique', 'Authentification', '57,7 % des authentifications échouent',
        nf(294763) + ' vérifications refusées, toutes chez un seul partenaire.', 'Analyser les échecs', 'Usage.dc.html'),
      al('Critique', 'IDPS', '14 ordres IDPS sur 14 en échec',
        '14 cartes non produites par ce circuit.', 'Examiner les erreurs', 'Idps.dc.html'),
      al('Priorité élevée', 'Cartes', nf(1330794) + ' cartes expédiées non remises',
        '42,9 % des cartes produites n’ont pas atteint leur titulaire.', 'Localiser les cartes', 'Cartes.dc.html'),
      al('Priorité élevée', 'Enrôlement', nf(118402) + ' paquets bloqués depuis plus de 30 jours',
        '3,6 % des inscrits attendent toujours leur NIU.', 'Voir les paquets bloqués', 'Technique.dc.html')
    ];
    const watch = [
      al('À surveiller', 'ABIS', nf(2353) + ' dossiers en attente d’adjudication',
        nf(640) + ' attendent depuis plus de 7 jours : leur NIU est bloqué.', 'Voir l’adjudication', 'Biometrie.dc.html#adjudication'),
      al('À surveiller', 'Cartes', nf(11835) + ' demandes d’impression en attente',
        'Cartes pas encore lancées en production.', 'Voir les demandes', 'Cartes.dc.html')
    ];

'''
SCRIPT = swap(SCRIPT, _old_alerts_js, _new_alerts_js)
SCRIPT = swap(SCRIPT, "{ label: 'Authentifications réussies', value: '42,3 %', detail: nf(215736) + ' sur ' + nf(510499) + ' requêtes', cta: 'Détail des authentifications', href: 'Usage.dc.html' }",
              "{ label: 'Taux de remise des cartes expédiées', value: '57,1 %', detail: nf(1770796) + ' remises sur ' + nf(3101590) + ' expédiées', cta: 'Détail des cartes', href: 'Cartes.dc.html' }")
SCRIPT = swap(SCRIPT, 'return { steps: steps, alerts: alerts, tiles: tiles,', 'return { steps: steps, actions: actions, watch: watch, tiles: tiles,')

# ---------- 6 : écart à la moyenne et seuil de 50 % ----------
_cols_old = 'grid-template-columns: minmax(110px, 1fr) 100px 100px 100px minmax(170px, 1.6fr) 64px; gap: 14px'
_cols_new = 'grid-template-columns: minmax(100px, 1fr) 84px 84px 84px minmax(160px, 1.6fr) 76px; gap: 12px'
BODY = swap(BODY, _cols_old, _cols_new, 2)
BODY = swap(BODY, '<span role="columnheader">Inscrits avec carte</span><span role="columnheader" style="text-align: right">Rejets</span>',
            '<span role="columnheader">Inscrits avec carte</span>'
            '<span role="columnheader" style="text-align: right">Écart à la moyenne</span>')
BODY = swap(BODY, '<span style="flex-grow: 1; height: 12px; background: #E3EAF3; border-radius: 0 4px 4px 0"><span style="display: block; height: 12px; width: {{r.w}}%; background: #2A78D6; border-radius: 0 4px 4px 0"></span></span>',
            '<span style="position: relative; flex-grow: 1; height: 12px; background: #E3EAF3; border-radius: 0 4px 4px 0"><span style="display: block; height: 12px; width: {{r.w}}%; background: #2A78D6; border-radius: 0 4px 4px 0"></span>'
            '<span aria-hidden="true" style="position: absolute; left: 50%; top: -4px; width: 2px; height: 20px; background: #071B35"></span></span>')
BODY = swap(BODY, '<span style="width: 52px; text-align: right; font-weight: {{r.cardWeight}}">{{r.part}}</span>',
            '<span style="width: 70px; display: inline-flex; justify-content: flex-end; align-items: center; gap: 4px; font-weight: {{r.cardWeight}}">'
            '<sc-if value="{{r.under}}" hint-placeholder-val="{{false}}"><svg width="12" height="12" viewBox="0 0 24 24" role="img" aria-label="Sous le seuil de 50 %" style="fill: #D03B3B"><path d="M12 2 1 21h22L12 2z"></path></svg></sc-if>{{r.part}}</span>')
BODY = swap(BODY, '<span role="cell" style="text-align: right">{{r.rej}}</span>',
            '<span role="cell" style="text-align: right; font-weight: 500">{{r.ecart}}</span>')
BODY = swap(BODY, 'Part des inscrits qui ont reçu leur carte : de 41,9 % en Savanes à 67,6 % dans le Grand Lomé.',
            'Part des inscrits qui ont reçu leur carte, comparée à la moyenne nationale de 54,0 % et au seuil de vigilance de 50 %.')

SCRIPT = swap(SCRIPT, "part: pct(part), w: part.toFixed(1), rej: pct(r[5]),\n        cardWeight: part < 45 ? '600' : '400',",
              "part: pct(part), w: part.toFixed(1), ecart: ((part - natAvg) >= 0 ? '+' : '−') + Math.abs(part - natAvg).toFixed(1).replace('.', ',') + ' pts',\n        under: part < 50, cardWeight: part < 50 ? '600' : '400',")
SCRIPT = swap(SCRIPT, '    const regions = regs.map((r) => {\n      const part = r[4] / r[2] * 100;',
              '    const natAvg = regs.reduce((a, r) => a + r[4], 0) / regs.reduce((a, r) => a + r[2], 0) * 100;\n'
              '    const regions = regs.map((r) => {\n      const part = r[4] / r[2] * 100;')

BODY = swap(BODY, '<div style="flex: 0 1 580px; max-width: 100%; min-width: 0">', '<div style="flex: 0 1 540px; max-width: 100%; min-width: 0">')
BODY = swap(BODY, '<div role="table" aria-label="Parcours par région" style="min-width: 640px;', '<div role="table" aria-label="Parcours par région" style="min-width: 660px;')
_legende = ('<div style="display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 4px 20px; padding: 10px 8px 0; border-top: 1px solid #EEF2F5; font-size: 12px; color: #4B5A6E">'
            '<span style="display: inline-flex; align-items: center; gap: 6px"><span aria-hidden="true" style="width: 2px; height: 14px; background: #071B35"></span>Seuil de vigilance : 50 %</span>'
            '<span style="display: inline-flex; align-items: center; gap: 6px"><svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true" style="fill: #D03B3B"><path d="M12 2 1 21h22L12 2z"></path></svg>Sous le seuil</span>'
            '<span>Écart en points par rapport à la moyenne nationale (54,0 %)</span></div>\n')
BODY = swap(BODY, '</sc-for>\n</div>\n<div style="margin-top: 20px; display: grid;', '</sc-for>\n' + _legende + '</div>\n<div style="margin-top: 20px; display: grid;')

# ---------- v4.3 : vue d'ensemble de tous les KPI, un bloc par onglet ----------
import p_bio as BIO

_SEVCHIP = {'Critique': ('#FCEBEB', '#6E1414', '#D03B3B'), 'Priorité élevée': ('#FDEEE7', '#7A3413', '#EC835A'), 'À surveiller': ('#FEF4DC', '#664700', '#FAB219')}


def _chip(level):
    bg, fg, ic = _SEVCHIP[level]
    return (f'<span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 8px; border-radius: 4px; background: {bg}; color: {fg}; font-size: 12px; font-weight: 600; white-space: nowrap">'
            f'<svg width="12" height="12" viewBox="0 0 24 24" aria-hidden="true" style="fill: {ic}"><path d="M12 2 1 21h22L12 2z"></path></svg>{level}</span>')


_TEST_CHIP = ('<span style="display: inline-flex; align-items: center; padding: 3px 8px; border-radius: 4px; background: #FCBA21; color: #071B35; '
              'font-size: 12px; font-weight: 600; white-space: nowrap">Données de test</span>')

_ICO = 'width="26" height="26" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; fill: none; stroke: #013781; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round"'
MOD_ICONS = {
    'enrol': f'<svg {_ICO}><circle cx="9" cy="8" r="4"></circle><path d="M2 21c0-4 3-7 7-7s7 3 7 7"></path><path d="M19 8v6M16 11h6"></path></svg>',
    'cartes': f'<svg {_ICO}><rect x="2" y="5" width="20" height="14" rx="2"></rect><circle cx="8" cy="12" r="2.5"></circle><path d="M13 10h6M13 14h4"></path></svg>',
    'abis': BIO.ICONS['finger'],
    'idps': f'<svg {_ICO}><path d="M6 9V3h12v6"></path><rect x="3" y="9" width="18" height="8" rx="2"></rect><path d="M7 14h10v7H7z"></path></svg>',
    'auth': f'<svg {_ICO}><path d="M12 2 4 5v6c0 5 3.5 9 8 11 4.5-2 8-6 8-11V5l-8-3z"></path><path d="M8.5 12l2.5 2.5L16 9.5"></path></svg>',
    'tech': f'<svg {_ICO}><rect x="5" y="3" width="14" height="18" rx="2"></rect><path d="M9 3v2h6V3"></path><path d="M8.5 12l2 2 4-4"></path><path d="M9 17h6"></path></svg>',
}


def _val(v, sub=''):
    return v + (f' <span style="font-weight: 400; color: #4B5A6E">{sub}</span>' if sub else '')


def mod_card(key, name, href, cta, big, big_label, rows, level=None, test=False, big_color='#071B35'):
    chips = (_chip(level) if level else '') + (_TEST_CHIP if test else '')
    return (f'<article aria-labelledby="mod-{key}" style="border: 1px solid #DCE3E9; border-radius: 8px; padding: 20px 22px; display: flex; flex-direction: column; gap: 12px; min-width: 0">'
            f'<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px; min-height: 30px">'
            f'<div style="display: flex; align-items: center; gap: 10px">{MOD_ICONS[key]}<h3 id="mod-{key}" style="margin: 0; font-size: 16px; font-weight: 600">{name}</h3></div>'
            f'<div style="display: flex; flex-wrap: wrap; gap: 6px">{chips}</div></div>'
            f'<div style="display: flex; flex-direction: column"><span style="font-size: 30px; font-weight: 600; letter-spacing: -0.01em; line-height: 1.2; color: {big_color}">{big}</span>'
            f'<span style="font-size: 13px; color: #4B5A6E">{big_label}</span></div>'
            '<ul style="list-style: none; margin: 0; padding: 0; font-variant-numeric: tabular-nums">'
            + ''.join(f'<li style="display: flex; justify-content: space-between; align-items: baseline; gap: 12px; padding: 7px 0; border-top: 1px solid #EEF2F5">'
                      f'<span style="font-size: 13px; color: #4B5A6E">{l}</span><span style="font-size: 14px; font-weight: 600; text-align: right; white-space: nowrap">{v}</span></li>' for l, v in rows)
            + '</ul>'
            f'<a href="{href}" style="margin-top: auto; display: inline-flex; align-items: center; min-height: 44px; font-size: 13px; font-weight: 600">{cta}</a></article>')


_q = BIO
MODULE_CARDS = [
    mod_card('enrol', 'Enrôlement', 'Enrolement.dc.html', 'Voir l’enrôlement', '3 278 239', 'inscriptions', [
        ('Pré-inscriptions', '606 850'),
        ('NIU générés', _val('3 058 886', '93,3 %')),
        ('Délai médian jusqu’au NIU', '6,5 jours'),
        ('Paquets rejetés', _val('86 496', '2,6 %')),
        ('Mises à jour et récupérations', '14 740')], level='Priorité élevée'),
    mod_card('cartes', 'Cartes', 'Cartes.dc.html', 'Voir les cartes', '1 770 796', 'cartes remises aux citoyens', [
        ('Demandes d’impression', '3 113 431'),
        ('Cartes imprimées et expédiées', '3 101 590'),
        ('Cartes à remettre', '1 330 794'),
        ('Taux de remise', '57,1 %'),
        ('Délai médian du NIU à la carte', '34 jours')], level='Priorité élevée'),
    mod_card('abis', 'ABIS', 'Biometrie.dc.html', 'Voir l’ABIS', BIO.nf(BIO.DEDUP), 'recherches de doublons', [
        ('Inscriptions passées par l’ABIS', BIO.pct(BIO.DEDUP / BIO.INSCRIPTIONS * 100)),
        ('Doublons confirmés (HIT)', BIO.nf(BIO.HIT)),
        ('En attente d’adjudication', BIO.nf(BIO.ADJ_ATTENTE)),
        ('Taux d’erreur', BIO.pct((BIO.ERR_ID + BIO.ERR_INS) / (BIO.DEDUP + BIO.INSERT) * 100, 2)),
        ('Empreintes de qualité excellente', f"{BIO.Q_FINGER['levels'][2]} %")], level='À surveiller', test=True),
    mod_card('idps', 'IDPS', 'Idps.dc.html', 'Voir l’IDPS', '14', 'ordres d’impression reçus', [
        ('En attente', '14'),
        ('Cartes imprimées', '0'),
        ('Taux d’échec', '100 %'),
        ('Erreurs de production', '14'),
        ('Dernier ordre', '03/07/2026')], level='Critique'),
    mod_card('auth', 'Authentifications', 'Usage.dc.html', 'Voir les authentifications', '510 499', 'requêtes d’authentification', [
        ('Réussies', _val('215 736', '42,3 %')),
        ('Échouées', _val('294 763', '57,7 %')),
        ('Requêtes biométriques', '96,0 %'),
        ('Requêtes par code à usage unique', '3,6 %'),
        ('Partenaires raccordés', '1')], level='Critique'),
    mod_card('tech', 'Qualité et technique', 'Technique.dc.html', 'Voir la qualité et la technique', '261 jours', 'sans nouvelles données', [
        ('Contrôles non conformes', '3'),
        ('Contrôles à vérifier', '2'),
        ('Contrôles conformes', '2'),
        ('Compteurs faux dans le BI actuel', '3'),
        ('Paquets bloqués depuis plus de 30 jours', '118 402')], big_color='#8A1F1F'),
]

MODULES = ('<section aria-labelledby="modules" style="' + CARD + '; display: flex; flex-direction: column; gap: 16px">\n'
           '<div><h2 id="modules" style="' + H2 + '">Indicateurs clés par module</h2>'
           '<p style="' + SUB + '">Les chiffres principaux de chaque onglet ; la pastille reprend l’alerte la plus grave du module.</p></div>\n'
           '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(340px, 100%), 1fr)); gap: 16px">\n'
           + '\n'.join(MODULE_CARDS) + '\n</div>\n</section>')

_seg_start = BODY.index('</section>') + len('</section>')
_seg_end = BODY.index('<section aria-labelledby="regions"')
BODY = BODY[:_seg_start] + '\n\n' + MODULES + '\n\n' + ALERTES.replace('flex: 1 1 520px; min-width: 0; ', '') + '\n\n' + BODY[_seg_end:]
assert BODY.count('aria-label="Indicateurs clés"') == 0 and BODY.count('id="qualite"') == 0

# ---------- styles propres à la V2 ----------
CSS = ('.alerte{display:grid;grid-template-columns:128px minmax(0,1fr) auto;gap:8px 16px;align-items:center;padding:14px 0;border-top:1px solid #E6EBEF}'
       '.alerte-action{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 14px;box-sizing:border-box;border:1px solid #013781;border-radius:6px;font-size:13px;font-weight:600;color:#013781;text-decoration:none;white-space:nowrap}'
       '.alerte-action:hover{background:#013781;color:#FFFFFF}'
       '.qrow{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:12px 0;border-top:1px solid #E6EBEF}'
       '@media (max-width:700px){.alerte{grid-template-columns:minmax(0,1fr)}.alerte>div:first-child{flex-direction:row !important;align-items:center !important;gap:8px !important}.alerte-action{justify-self:start}.qrow{flex-wrap:wrap}}')



def build():
    html = page('Vue d’ensemble du parcours citoyen', 'Main.dc.html', p_main.FILTERS, BODY, SCRIPT, 3300, '')
    html = swap(html, '\n</style>\n</helmet>', '\n' + CSS + '\n</style>\n</helmet>')
    return html
