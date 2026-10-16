# Extraction depuis MOSIP

But : copier dans le schéma `brut` de la base BI les seules tables MOSIP utiles (liste dans `docs/sources-mosip.md`),
avec un compte MOSIP **en lecture seule**. Aucune écriture sur les bases MOSIP.

Options, de la plus simple à la plus fine :
1. Extraction nocturne (`pg_dump --data-only -t ...` ou `COPY ... TO STDOUT`), rechargement complet du schéma `brut`.
2. Réplication logique PostgreSQL des tables utiles vers `brut`.
3. Capture des changements (Debezium + Kafka), déjà proposée par le module de reporting de MOSIP.

À trancher avec l'équipe MOSIP de l'ANID (volumétrie, fenêtre de maintenance, accès réseau), puis consigner dans
`docs/decisions.md`. Colonnes sensibles (nom, NIU, biométrie) : ne pas les extraire.
