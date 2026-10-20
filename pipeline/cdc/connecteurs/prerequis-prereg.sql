-- Prérequis du connecteur bi-cdc-prereg sur la base mosip_prereg (préparé par Claude, à faire exécuter par le DBA).
-- Décision du 20/10/2026 (docs/decisions.md) : capture de prereg.applicant_demographic et
-- prereg.applicant_demographic_consumed limitée aux colonnes prereg_id, status_code, cr_dtimes, upd_dtimes. Les
-- colonnes d'identité (demog_detail, demog_detail_hash, cr_appuser_id) ne sont jamais lues.
-- Partie A : contrôles en lecture, sans effet. Partie B : commandes commentées, à exécuter une par une en recette puis
-- en production après validation explicite de chacune. Aucune n'est destructive ; aucun mot de passe ne figure ici.

-- =====================================================================================================
-- A. Contrôles (lecture seule)
-- =====================================================================================================
show wal_level;                       -- attendu : logical
show max_replication_slots;           -- un slot de plus que les slots existants
show max_wal_senders;
show max_slot_wal_keep_size;          -- -1 = illimité : risque de saturation disque, à borner

-- Clé primaire et replica identity des deux tables (DEFAULT suffit avec une clé primaire).
select n.nspname as schema_name, c.relname as table_name, c.relreplident as replica_identity,
       exists (select 1 from pg_index i where i.indrelid = c.oid and i.indisprimary) as has_primary_key
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'prereg' and c.relname in ('applicant_demographic', 'applicant_demographic_consumed');

-- Colonnes réelles des deux tables (comparer au DDL v1.1.5 de pipeline/sources/ddl/mosip_prereg/).
select table_name, column_name, data_type
from information_schema.columns
where table_schema = 'prereg' and table_name in ('applicant_demographic', 'applicant_demographic_consumed')
order by table_name, ordinal_position;

-- Codes de statut présents (à faire valider : pipeline.correspondance_statut_preinscription). Comptages seuls.
select 'demande' as table_source, status_code, count(*) from prereg.applicant_demographic group by status_code
union all
select 'consommee', status_code, count(*) from prereg.applicant_demographic_consumed group by status_code
order by 1, 3 desc;

-- Publications et slots existants (une publication dbz_publication existe déjà sur l'instance : ne pas la réutiliser).
select pubname, puballtables from pg_publication;
select * from pg_publication_tables where schemaname = 'prereg';
select slot_name, plugin, active, wal_status from pg_replication_slots;

-- =====================================================================================================
-- B. Commandes DBA (validation explicite requise, une par une)
-- =====================================================================================================
-- B1. Rôle dédié (le même que pour mosip_regprc s'il existe déjà), sans superutilisateur.
-- grant connect on database mosip_prereg to bi_cdc;
-- grant usage on schema prereg to bi_cdc;
-- SELECT limité aux colonnes capturées : le snapshot initial ne lit que celles-ci.
-- grant select (prereg_id, status_code, cr_dtimes, upd_dtimes) on prereg.applicant_demographic to bi_cdc;
-- grant select (prereg_id, status_code, cr_dtimes, upd_dtimes) on prereg.applicant_demographic_consumed to bi_cdc;

-- B2. Publication explicite, limitée aux colonnes (PostgreSQL 15 et plus ; sinon publication des deux tables et
--     filtrage par column.include.list du connecteur seulement — à décider avec le DBA selon la version d'EDB).
-- create publication bi_cdc_prereg
--     for table prereg.applicant_demographic (prereg_id, status_code, cr_dtimes, upd_dtimes),
--               prereg.applicant_demographic_consumed (prereg_id, status_code, cr_dtimes, upd_dtimes);

-- Retour arrière (connecteur arrêté, après validation) :
-- drop publication bi_cdc_prereg;  -- le slot bi_cdc_prereg_<env> se supprime à part (voir le runbook du skill)
