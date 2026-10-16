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
           '<span style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap">' + ICO_W + '<strong style="font-weight: 600">3</strong> à vérifier</span>'
           '<span style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap">' + ICO_OK + '<strong style="font-weight: 600">1</strong> conforme</span></span>')
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
      al('À surveiller', 'ABIS', 'Adjudication non alimentée',
        nf(16002) + ' rejets pour doublon, aucun passé en adjudication.', 'Vérifier le circuit', 'Biometrie.dc.html'),
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

# ---------- styles propres à la V2 ----------
CSS = ('.alerte{display:grid;grid-template-columns:128px minmax(0,1fr) auto;gap:8px 16px;align-items:center;padding:14px 0;border-top:1px solid #E6EBEF}'
       '.alerte-action{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 14px;box-sizing:border-box;border:1px solid #013781;border-radius:6px;font-size:13px;font-weight:600;color:#013781;text-decoration:none;white-space:nowrap}'
       '.alerte-action:hover{background:#013781;color:#FFFFFF}'
       '.qrow{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:12px 0;border-top:1px solid #E6EBEF}'
       '@media (max-width:700px){.alerte{grid-template-columns:minmax(0,1fr)}.alerte>div:first-child{flex-direction:row !important;align-items:center !important;gap:8px !important}.alerte-action{justify-self:start}.qrow{flex-wrap:wrap}}')



def build():
    html = page('Vue d’ensemble du parcours citoyen', 'Main.dc.html', p_main.FILTERS, BODY, SCRIPT, 2430, '')
    html = swap(html, '\n</style>\n</helmet>', '\n' + CSS + '\n</style>\n</helmet>')
    return html
