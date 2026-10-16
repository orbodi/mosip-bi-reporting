# Journaux ABIS et IDPS

Scripts à écrire pour lire les journaux ABIS d'IN Groupe (`auditlog.log` des 3 nœuds BRS, `quality.<date>.log` des
2 nœuds MBSS) et charger des agrégats dans le schéma `brut` (règles de calcul : `docs/indicateurs.md`, section ABIS ;
points d'attention : `docs/sources-mosip.md`). Dédoublonner par `requestId`, pseudonymiser les agents, ne garder ni
commentaire libre ni RID complet.
