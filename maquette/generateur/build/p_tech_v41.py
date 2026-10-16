import re, pathlib
from common import *

SRC = pathlib.Path(__file__).resolve().parent / 'src_v21'
_t = (SRC / 'Technique.dc.html').read_text()
CONTENT = re.search(r'(<section aria-labelledby="etapes".*?)\n<p style="margin: 0; font-size: 13px; color: #4B5A6E">Maquette v2\.1', _t, re.S).group(1)
SCRIPT = re.search(r'(class Component extends DCLogic \{.*\})\s*</script>', _t, re.S).group(1)

FILTERS = PERIODE + REGION + DIVIDER + select('Type de demande', ['Toutes les demandes', 'Nouvelle inscription', 'Mise à jour', 'Récupération de NIU'], min_w=190)

I_FAIL = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; margin-top: 2px; fill: none; stroke: #D03B3B; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round"><circle cx="12" cy="12" r="10"></circle><line x1="9" y1="9" x2="15" y2="15"></line><line x1="15" y1="9" x2="9" y2="15"></line></svg>'
I_WARN = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; margin-top: 2px; fill: #FAB219; stroke: none"><path d="M12 2 1 21h22L12 2z"></path></svg>'
I_OK = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink: 0; margin-top: 2px; fill: none; stroke: #0CA30C; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round"><circle cx="12" cy="12" r="10"></circle><polyline points="8 12.5 11 15.5 16 9.5"></polyline></svg>'


def check(icon, status, rule, value):
    return ('<li style="display: flex; gap: 10px; align-items: flex-start; padding: 12px 0; border-top: 1px solid #EEF2F5">%s'
            '<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 12px; font-weight: 600">%s</span>'
            '<span style="font-size: 14px; font-weight: 500">%s</span><span style="font-size: 13px; color: #4B5A6E">%s</span></div></li>\n'
            % (icon, status, rule, value))


def fresh(module, last, refresh, gap):
    return ('<div role="row" style="display: grid; grid-template-columns: minmax(130px, 1fr) minmax(170px, 1.3fr) 150px 100px; gap: 12px; align-items: center; padding: 10px 0; border-top: 1px solid #EEF2F5">'
            '<span role="rowheader" style="font-weight: 500">%s</span><span role="cell">%s</span><span role="cell" style="color: #4B5A6E">%s</span>'
            '<span role="cell" style="text-align: right; font-weight: 600; color: #8A1F1F">%s</span></div>\n' % (module, last, refresh, gap))


CONTROLS = '''<div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: stretch">
<section aria-labelledby="fraicheur" style="flex: 1 1 560px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 8px">
<div>
<h2 id="fraicheur" style="''' + H2 + '''">Fraîcheur des données, source par source</h2>
<p style="''' + SUB + '''">Le BI se rafraîchit chaque jour, mais aucune source ne reçoit de nouvelles données.</p>
</div>
<div style="overflow-x: auto">
<div role="table" aria-label="Fraîcheur des données par module" style="min-width: 560px; font-variant-numeric: tabular-nums">
<div role="row" style="display: grid; grid-template-columns: minmax(130px, 1fr) minmax(170px, 1.3fr) 150px 100px; gap: 12px; padding: 6px 0; font-size: 12px; color: #4B5A6E">
<span role="columnheader">Module</span><span role="columnheader">Dernier événement reçu</span><span role="columnheader">Rafraîchissement du BI</span><span role="columnheader" style="text-align: right">Sans données</span>
</div>
''' + fresh('Enrôlement', '14/01/2026 à 11h42', '30/09/2026 à 23h00', '261 jours') \
    + fresh('Impression des cartes', '14/01/2026 à 11h59, un rejet le 13/03/2026', '01/10/2026 à 09h00', '261 jours') \
    + fresh('Authentification', '14/01/2026 à 11h05', '01/10/2026 à 09h00', '261 jours') \
    + fresh('Pré-inscription', '14/01/2026 à 11h28', '01/10/2026 à 09h00', '261 jours') \
    + fresh('Scores biométriques', '29/06/2026 à 15h15', '02/10/2026 à 08h00', '95 jours') \
    + fresh('IDPS', '03/07/2026 à 17h09', '02/10/2026 à 09h00', '91 jours') \
    + fresh('Transactions ABIS', '13/07/2026 à 11h59', '02/10/2026 à 08h00', '81 jours') \
    + fresh('Adjudication', 'Aucun événement', '02/10/2026 à 08h00', '—') + '''</div>
</div>
<p style="margin: auto 0 0; font-size: 12px; color: #4B5A6E">Le rejet d’impression du 13 mars laisse penser qu’au moins une source a continué de fonctionner après janvier.</p>
</section>

<section aria-labelledby="controles" style="flex: 1 1 480px; min-width: 0; ''' + CARD + '''; display: flex; flex-direction: column; gap: 4px">
<div>
<h2 id="controles" style="''' + H2 + '''">Contrôles de cohérence</h2>
<p style="''' + SUB + '''">Règles vérifiées à chaque rafraîchissement, avec la valeur qui les met en défaut.</p>
</div>
<ul style="list-style: none; margin: 8px 0 0; padding: 0">
''' + check(I_FAIL, 'Non conforme', 'Les dossiers « synchronisés mais non reçus » sont positifs ou nuls', 'Valeur actuelle : −16 734') \
    + check(I_FAIL, 'Non conforme', 'Le compteur des pré-inscriptions réservées correspond au graphique', '0 sur le compteur, environ 546 964 sur le graphique') \
    + check(I_WARN, 'À vérifier', 'Les cartes imprimées ne dépassent pas les NIU générés et les réimpressions', 'Écart de +42 704 cartes') \
    + check(I_WARN, 'À vérifier', 'Les cartes expédiées par centre ne dépassent pas ses inscriptions', 'Dépassé pour 4 des 5 centres les plus actifs') \
    + check(I_FAIL, 'Non conforme', 'Un ordre d’impression IDPS en erreur ne reste pas « en attente »', '14 ordres à la fois en attente et en erreur') \
    + check(I_WARN, 'À vérifier', 'Les rejets pour doublon passent par l’adjudication', '16 002 rejets pour doublon, 0 dossier en adjudication') \
    + check(I_OK, 'Conforme', 'Réussies et échouées font le total des authentifications', '215 736 + 294 763 = 510 499') + '''</ul>
</section>
</div>
'''

BODY = title('Qualité des données et suivi technique') + CONTROLS + CONTENT

FOOTER = 'Maquette v3. Fraîcheur, contrôles de cohérence et totaux viennent du BI actuel. Étapes, sous-motifs, centres et autres types sont fictifs ; les numéros de centre sont des exemples.'


def build():
    return page('Qualité et technique', 'Technique.dc.html', FILTERS, BODY, SCRIPT, 3000, FOOTER)
