# MOSIP 1.1.5 : sources, schémas et règles de vérification

Faits relevés dans les DDL officiels au tag `v1.1.5` (vérification d'octobre 2026). Ils servent de point de départ,
pas de vérité : l'instance de l'ANID peut contenir des correctifs (1.1.5.x) ou des écarts locaux. Toujours confronter
au catalogue de l'instance avant d'écrire du code.

## Sommaire
1. Où trouver les DDL
2. Tables utiles au reporting d'enrôlement
3. Ce qui n'existe pas en 1.1.5
4. Inspecter le catalogue d'une instance
5. Classer les colonnes
6. Points à faire confirmer par l'équipe MOSIP

## 1. Où trouver les DDL

Chaque base `mosip_x` contient un schéma `x` (ex. `mosip_regprc` → schéma `regprc`).

| Base | Dépôt et chemin (tag `v1.1.5`) |
|---|---|
| `mosip_regprc` | `github.com/mosip/registration/tree/v1.1.5/db_scripts/mosip_regprc` (liste de déploiement : `mosip_regprc_ddl_deploy.sql`, tables dans `ddl/regprc-<table>.sql`) |
| `mosip_master`, `mosip_kernel`, `mosip_audit`, `mosip_iam`, `mosip_keymgr`, `mosip_regdevice`, `mosip_authdevice` | `github.com/mosip/commons/tree/v1.1.5/db_scripts/` |
| `mosip_idrepo`, `mosip_idmap`, `mosip_credential` | `github.com/mosip/id-repository/tree/v1.1.5/db_scripts/` |
| `mosip_prereg` | `github.com/mosip/pre-registration/tree/v1.1.5/db_scripts/mosip_prereg` |
| `mosip_ida` | `github.com/mosip/id-authentication/tree/v1.1.5/db_scripts/mosip_ida` |
| `mosip_pms` | `github.com/mosip/partner-management-services/tree/v1.1.5/db_scripts/mosip_pms` |

Copier les fichiers utiles dans `pipeline/sources/ddl/<base>/` avec, en tête, le dépôt, le tag et la date de copie.
Si l'instance a été mise à jour (1.1.5.x), prendre le tag correspondant ou un `pg_dump --schema-only` fourni par le DBA.

## 2. Tables utiles au reporting d'enrôlement

Colonnes relevées dans `regprc` (v1.1.5, identiques en v1.1.5.5). Toutes les tables, sauf `reg_bio_ref`, ont aussi
`lang_code`, `cr_by`, `upd_by` et `del_dtimes`.

| Table | Colonnes (DDL v1.1.5) | Usage pour le BI |
|---|---|---|
| `regprc.registration` | `id`, `reg_type`, `ref_reg_id`, `applicant_type`, `status_code`, `status_comment`, `latest_trn_id`, `latest_trn_type_code`, `latest_trn_status_code`, `latest_trn_dtimes`, `reg_process_retry_count`, `reg_stage_name`, `trn_retry_count`, `pkt_cr_dtimes`, `is_active`, `cr_dtimes`, `upd_dtimes`, `is_deleted` | Inscriptions, devenir (statut), type d'opération, étape bloquante |
| `regprc.registration_list` | `id`, `reg_id`, `reg_type`, `packet_checksum`, `packet_size`, `client_status_code`, `client_status_comment`, `additional_info`, `status_code`, `status_comment`, `cr_dtimes` | Paquets synchronisés (écart synchronisés / reçus) |
| `regprc.registration_transaction` | `id`, `reg_id`, `trn_type_code`, `remarks`, `parent_regtrn_id`, `ref_id`, `ref_id_type`, `status_code`, `sub_status_code`, `status_comment`, `cr_dtimes` | Étapes et ancienneté des paquets en cours ; motifs de rejet |
| `regprc.reg_manual_verification` | clé (`reg_id`, `matched_ref_id`, `matched_ref_type`), `mv_usr_id`, `ref_regtrn_id`, `request_id`, `res_text`, `status_code`, `reason_code`, `status_comment`, `trntyp_code`, `is_active`, `cr_dtimes` | Vérification manuelle (adjudication côté MOSIP) |
| `regprc.abis_request` | `id`, `req_batch_id`, `abis_app_code`, `request_type`, `request_dtimes`, `bio_ref_id`, `ref_regtrn_id`, `req_text`, `status_code`, `status_comment` | Requêtes ABIS vues par MOSIP (contrôle croisé avec les journaux IN Groupe) |
| `regprc.abis_response` | `id`, `abis_req_id`, `resp_dtimes`, `resp_text`, `status_code`, `status_comment` | Réponses ABIS |
| `regprc.reg_bio_ref` | `reg_id` (clé), `bio_ref_id`, `is_active` | Correspondance RID ↔ référence biométrique |
| `master.registration_center` | clé (`id`, `lang_code`), `cntrtyp_code`, `latitude`, `longitude`, `location_code`, `holiday_loc_code`, `zone_code`, `is_active`… | Centre → localisation |
| `master.location` | clé (`code`, `lang_code`), `name`, `hierarchy_level`, `hierarchy_level_name`, `parent_loc_code`, `is_active` | Hiérarchie territoriale (attention : la colonne s'appelle `code`, pas `location_code`) |
| `master.loc_hierarchy_list` | `hierarchy_level`, `hierarchy_level_name`… | Libellés des niveaux (région, préfecture…) |

Pièges connus :
- `registration` porte deux familles de statut : `status_code` (statut du paquet) et `latest_trn_status_code`
  (statut de la dernière transaction). Le BI actuel les mélange (statuts en doublon). Choisir et documenter.
- Les tables `master` sont multilingues : la clé contient `lang_code`. Filtrer sur une langue de référence, sinon
  chaque centre ou lieu est compté plusieurs fois.
- Les codes de statut, de type (`reg_type`) et de transaction ne sont pas listés ici : les relever sur l'instance
  (`select status_code, count(*) ... group by 1`) et les faire valider ; ne jamais supposer une liste.
- Le RID (`registration.id`) commence, selon la convention MOSIP, par l'identifiant du centre puis celui de la
  machine. Vérifier sur un échantillon que le préfixe retrouve bien `master.registration_center.id` avant de s'en
  servir, et ne pas conserver le RID complet dans le Data Mart.

## 3. Ce qui n'existe pas en 1.1.5

- **`anonymous_profile`** : absente des listes de déploiement `regprc` et `idrepo` au tag `v1.1.5`.
  `idrepo.anonymous_profile` apparaît au tag `v1.1.5.5` ; `regprc.anonymous_profile` en 1.2.0.
  Conséquence : sexe, âge et autres attributs démographiques n'ont pas de source anonymisée en 1.1.5.
  Options à présenter (décision humaine) : vérifier si l'instance est en 1.1.5.5 ; mise à niveau ; flux anonymisé
  produit par MOSIP. Ne jamais proposer de déchiffrer `uin_data` ou des paquets.
- **Pas de source démographique utilisable.** La seule colonne de sexe repérée dans `regprc` en 1.1.5 est dans
  `regprc.individual_demographic_dedup` (table de déduplication démographique), qui contient aussi des données
  d'identité en clair (nom, date de naissance, coordonnées ; vérifier la liste exacte dans le DDL). Table
  **interdite** de capture, même pour une seule colonne : la tentation est forte, la réponse est une décision
  (source anonymisée), pas un contournement.
- **Pas de composant de reporting livré avec 1.1.5.** Le dépôt `mosip/reporting` (branche `1.1.5` comprise) vise
  1.2.0 (`anonymous_profile`, Elasticsearch/Kibana) ; ne pas reprendre sa configuration telle quelle.

## 4. Inspecter le catalogue d'une instance

Utiliser [../assets/inventaire-catalogue.sql](../assets/inventaire-catalogue.sql), en lecture seule, sur une
réplique ou un environnement de recette. Il liste tables, colonnes, types, clés primaires, `REPLICA IDENTITY`,
volumes estimés et publications existantes. Le résultat (sans données) peut être versionné dans
`pipeline/sources/catalogue/`.

Règle : si une table ou une colonne n'apparaît ni dans un DDL de `pipeline/sources/ddl/` ni dans un inventaire
versionné, elle n'est pas utilisable dans le code. Demander l'information.

## 5. Classer les colonnes

Pour chaque colonne candidate, une des trois classes, notée dans la fiche de la source :

| Classe | Exemples dans les tables ci-dessus | Traitement |
|---|---|---|
| Nécessaire | `reg_type`, `status_code`, `latest_trn_status_code`, `cr_dtimes`, `upd_dtimes`, `is_deleted`, `location_code`, `hierarchy_level`, `parent_loc_code` | Capturée telle quelle |
| Identifiante | `registration.id` (RID), `reg_id`, `bio_ref_id`, `mv_usr_id`, `request_id` | Attributs dérivés (centre, machine, date) puis empreinte HMAC dans Spark (clé primaire, que Debezium ne masque pas dans la clé du message) ou empreinte salée Debezium (colonne hors clé) ; jamais en clair dans le Data Mart |
| Interdite | `req_text`, `resp_text`, `res_text`, `additional_info`, `status_comment`, `remarks`, `client_status_comment` (textes libres ou contenus de requêtes) ; toute colonne de `regprc.individual_demographic_dedup` et des tables d'identité (`idrepo.uin*`, documents, biométrie) | Exclue de la capture (`column.include.list` sans elles ; tables absentes de `table.include.list`) |

Le classement « interdite » des textes libres est prudent : ils peuvent contenir des identifiants ou des extraits de
requêtes. Une exception se décide avec la sécurité et s'écrit dans `docs/decisions.md`.

## 6. Points à faire confirmer par l'équipe MOSIP

- Version exacte déployée (1.1.5 ou 1.1.5.x) et écarts locaux au DDL.
- Liste des `status_code`, `latest_trn_status_code`, `reg_type`, `trn_type_code` réellement présents, et la règle
  « aboutie / rejetée / échouée / en cours » attendue par l'ANID.
- Source acceptable pour sexe et âge.
- Fuseau des horodatages (`cr_dtimes`…) : UTC ou heure locale (Lomé est en UTC+0, mais la règle doit être écrite).
- Tables où des suppressions physiques ont lieu (purge, archivage) : elles changent l'interprétation des `d`.
