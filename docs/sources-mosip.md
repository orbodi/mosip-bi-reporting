# Sources de données

Synthèse des audits du BI existant (1er et 2 oct. 2026) et du document IN Groupe « Togo Eid, Reporting biométrique
BI ABIS » v0.2 (réf. 2025_2000090622, 23/01/2026). Les tables sont **probables** : à valider sur le schéma MOSIP
déployé à l'ANID avant d'écrire le pipeline. Relevé des DDL officiels v1.1.5 (colonnes, pièges, tables absentes) :
`references/mosip-115.md` du skill `mosip-bi-pipeline`.

## Bases MOSIP (PostgreSQL)
| Domaine | Tables probables | Indicateurs |
|---|---|---|
| Pré-inscription | `mosip_prereg.applicant_demographic` (exclue : données d'identité), `reg_appointment` | E-PRE, E-PRE-RDV |
| Enrôlement | `mosip_regprc.registration`, `registration_list`, `registration_transaction` | E-INS, E-COURS, E-REJ, E-MAJ… |
| Identité | `mosip_idrepo.uin` (exclue : NIU et données d'identité) ; pas de `anonymous_profile` en 1.1.5 | E-NIU, sexe, âge |
| Adjudication (MOSIP) | `mosip_regprc.reg_manual_verification` | contrôle croisé avec les journaux ABIS |
| Correspondance biométrique | `mosip_regprc.reg_bio_ref` (UUID ABIS ↔ RID) | ABIS par territoire |
| Cartes | `mosip_credential.credential_transaction` | I-DEM, I-REJ, I-EXP |
| Authentification | `mosip_ida.auth_transaction`, `mosip_pms.partner` | A-* |
| Référentiels | `master.location`, `master.registration_center` | territoire, centres |

Le module de reporting de MOSIP (dépôt `mosip/reporting` : Debezium, Kafka, Elasticsearch) vise MOSIP 1.2.0 et
`anonymous_profile` : ne pas le reprendre tel quel en 1.1.5. Le BI en reprend le principe (Debezium et Kafka) avec
PySpark et un Data Mart PostgreSQL (`docs/decisions.md`, 16/10/2026).

Tables exclues de la capture (données d'identité) : `regprc.individual_demographic_dedup`, `idrepo.uin*`,
`prereg.applicant_demographic`, `prereg.applicant_document`, documents et biométrie. Une exception se décide avec la
sécurité et s'écrit dans `docs/decisions.md`.

Astuce : le RID (29 chiffres) commence par l'identifiant du centre (5 chiffres) puis celui de la machine (5 chiffres),
suivis d'un compteur et d'un horodatage. On descend au centre et à la machine sans déchiffrer de données (préfixe à
vérifier sur un échantillon contre `master.registration_center`). Le pipeline dérive centre et machine puis remplace
le RID par une empreinte HMAC : le RID complet n'entre jamais dans le Data Mart.

## Journaux ABIS (IN Groupe)
Les KPI ABIS ne viennent pas de MOSIP mais des journaux de l'ABIS :
- `auditlog.log` des 3 nœuds BRS (brs1 à brs3, `/log/crudN/auditlogs/`) : à lire tous et à dédoublonner par `requestId` ;
- `quality.<date>.log` des 2 nœuds MBSS (`/opt/mbss/logs/quality/`).

Règles de calcul : voir la section ABIS de `docs/indicateurs.md`. Points d'attention :
- `ACTIVITY_RESULT` vaut SUCCESS même en erreur : se fier à `returnValue` (1 = traité, 2 = erreur) ;
- compter des dossiers, pas des candidats (HIT = `candidateList.count > 0`) ;
- délai de réponse par service avec les horodatages START et END d'un même `requestId` ;
- pour insert et identify, le `referenceId` est un UUID à relier au RID via `reg_bio_ref` ;
- noms d'agents et commentaires libres avec RID présents dans les journaux : pseudonymiser, ne jamais afficher tels quels.

Questions ouvertes à IN Groupe : signification de NBPK, des RqType autres que IP et des codes `failureReason` ;
échelle des scores (0–255 ?) et seuils Excellent / Moyen / Faible ; pourquoi le BI actuel ne voit qu'une journée ABIS.

## IDPS
Base du système IDPS (circuit pilote : 14 ordres, Savanes, 03/07/2026) et `credential_transaction`. Ordre des étapes
(personnalisation → contrôle qualité → supervision) supposé, à valider avec l'équipe IDPS.

## Fraîcheur par source (au 2 oct. 2026)
Enrôlement et cartes 14/01/2026 à 11h59 ; authentifications 14/01/2026 à 11h05 ; scores biométriques 29/06/2026 ;
IDPS 03/07/2026 à 17h09 ; ABIS 13/07/2026. La table `bi.source_fraicheur` porte ces dates ; chaque page affiche celle de sa source principale.

## Données personnelles
La base BI ne contient que des agrégats et des attributs non identifiants (territoire, date, sexe, tranche d'âge, type).
Pas de nom, pas de NIU, pas de RID complet, pas de donnée biométrique. Le rôle Debezium sur MOSIP a
`REPLICATION` et `SELECT` sur les seules tables capturées, sans superutilisateur ni droit d'écriture. Le RID passe en
clair dans la clé des messages Kafka (Debezium ne masque pas les clés) : accès aux topics réservé au pipeline.
