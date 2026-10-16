"""v3.4 : retrait des notes de maquette, consignes et commentaires d'analyste.

Chaque règle doit s'appliquer exactement une fois, sinon le build s'arrête.
Les notes retirées sont reportées dans la fiche projet (notes pour l'équipe technique).
"""
import re

S = re.DOTALL


def _pat(text):
    # les espaces du texte peuvent être des espaces insécables dans le HTML
    e = re.escape(text)
    return e.replace('\\ ', '[ \u00a0\u202f]') if '\\ ' in e else e.replace(' ', '[ \u00a0\u202f]')


def drop_p(key):
    """Supprime le paragraphe <p> qui contient le texte `key`."""
    return (r'<p[ >](?:(?!</p>).)*?' + _pat(key) + r'.*?</p>\n?', '')


def sub(old, new):
    return (_pat(old), new)


RULES = {
    'Main.dc.html': [
        sub("detail: 'Indicateur à créer à partir des dates de livraison'", "detail: 'Calculé sur les cartes livrées'"),
    ],
    'Enrolement.dc.html': [
        drop_p('Étape facultative : le citoyen remplit'),
        sub("detail: 'Lu sur le graphique : le compteur actuel affiche 0', warn: true", "detail: 'Estimation', warn: false"),
        sub("value: 'À créer', detail: 'Statut « consommée » à exposer pour mesurer la conversion'", "value: 'Non mesuré', detail: ''"),
        drop_p('synchronisés mais non reçus » est à recalculer'),
        sub('12 dernières semaines complètes. Survolez une semaine pour le détail.', '12 dernières semaines complètes.'),
        drop_p('La semaine du 12 janvier, incomplète'),
        sub('Couleur selon le taux de rejet. Cliquez sur une région pour afficher ses préfectures.', 'Couleur selon le taux de rejet.'),
        sub("tableHint: cur ? 'Niveaux suivants : commune, canton, localité, centre' : 'Choisissez une région pour voir ses préfectures'", "tableHint: ''"),
        drop_p('Niveau suivant : machine et opérateur'),
    ],
    'Cartes.dc.html': [
        sub('Barre : nombre de cartes. Choisissez une région pour afficher ses préfectures.', 'Barre : nombre de cartes.'),
        sub('Temps écoulé depuis l’expédition, à la date des dernières données.', 'Temps écoulé depuis l’expédition.'),
        drop_p('Croisement des deux classements actuels'),
        drop_p('Pistes à vérifier : réimpressions'),
    ],
    'Usage.dc.html': [
        drop_p('ne donne pas la cause des échecs'),
        drop_p('Volume de requêtes et part d’échecs pour chaque type.'),
        drop_p('ne montre que la part de chaque type'),
        drop_p('Regroupement proposé des codes d’erreur'),
        sub('12 dernières semaines complètes. Survolez une semaine pour le détail.', '12 dernières semaines complètes.'),
        drop_p('Un seul partenaire envoie des requêtes'),
        drop_p('Quand d’autres partenaires'),
    ],
    'Technique.dc.html': [
        drop_p('laisse penser qu’au moins une source'),
        drop_p('Règles vérifiées à chaque rafraîchissement'),
        drop_p('Quatre statuts lisibles à la place'),
        drop_p('À valider avec l\'équipe MOSIP'),
        drop_p('semble venir du statut de la dernière étape'),
        sub('86 496 demandes rejetées. Choisissez un motif pour le détailler.', '86 496 demandes rejetées.'),
        drop_p('Niveau suivant : détail par machine'),
    ],
}


def clean(name, html):
    for pat, rep in RULES.get(name, []):
        html, n = re.subn(pat, rep, html, flags=S)
        assert n == 1, (name, pat[:80], n)
    return html
