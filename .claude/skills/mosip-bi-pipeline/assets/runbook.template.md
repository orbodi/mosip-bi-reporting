# Runbook : pipeline CDC <domaine> (<environnement>)

> Modèle à compléter et à placer dans `docs/exploitation/`. Ne jamais y écrire de secret : seulement l'endroit où il
> est conservé.

## Fiche d'identité

| Élément | Valeur |
|---|---|
| Base source | `<mosip_regprc>` sur `<hôte, réplique ou primaire>` (EDB `<version>`) |
| Tables capturées | `<regprc.registration, ...>` |
| Publication / slot | `<publication>` / `<slot>` |
| Connecteur | `<nom>` sur Kafka Connect `<cluster>` ; configuration : `pipeline/cdc/connecteurs/<fichier>.json` |
| Topics | `<mosip.env.regprc.registration, ...>` (partitions, réplication, rétention) |
| Job Spark | `<module>` ; requête `<nom@génération>` ; checkpoint `<emplacement>` |
| Data Mart | `<base>` ; schémas `etat`, `pipeline`, `bi` |
| Secrets | `<coffre / fichier protégé>` (sel HMAC, mots de passe) |
| Responsables | DBA : `<nom>` ; Kafka : `<nom>` ; pipeline : `<nom>` ; métier : `<nom>` |

## Démarrage et arrêt

1. `<commandes de démarrage, dans l'ordre : Data Mart, topics, connecteur, job>`
2. Vérifications après démarrage : slot actif, `MilliSecondsBehindSource`, lots dans `pipeline.lot_traite`,
   contrôles qualité.
3. Arrêt : job Spark puis connecteur. Pause de plus de `<N>` heures : prévenir le DBA (WAL retenu).

## Surveillance

| Métrique | Seuil | Où la lire | Première action |
|---|---|---|---|
| WAL retenu par le slot | `<x Go>` | `<tableau de bord / requête>` | `<...>` |
| Retard CDC | `<x min>` | | |
| Lag Spark | `<x offsets>` | | |
| Rejets | `<n / heure>` | | |
| Fraîcheur BI | `<x min>` | | |

## Procédures d'incident

Pour chaque incident : symptôme, diagnostic, action, **qui valide**, retour arrière.

### WAL retenu en hausse
### Connecteur en échec
### Job Spark arrêté (perte d'offsets, TRUNCATE, seuil de rejets)
### Contrôle qualité en échec
### Changement de schéma MOSIP

## Procédures sensibles (validation écrite requise)

| Procédure | Qui valide | Préalables | Retour arrière |
|---|---|---|---|
| Snapshot incrémental d'une table | | | |
| Nouvelle génération de checkpoint | | rétention Kafka suffisante | ancienne génération conservée |
| Suppression / recréation du slot | DBA + responsable | connecteur arrêté | |
| Migration destructive du Data Mart | | sauvegarde vérifiée | |

## Historique des interventions

| Date | Intervenant | Action | Validation |
|---|---|---|---|
