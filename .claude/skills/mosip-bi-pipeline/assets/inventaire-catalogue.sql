-- Inventaire du catalogue d'une base MOSIP (lecture seule).
-- À exécuter par un DBA sur une réplique ou une recette, une base à la fois (ex. mosip_regprc), avec psql :
--   psql -X -A -F ';' -v schema=regprc -f inventaire-catalogue.sql > inventaire_regprc.csv
-- Ne lit aucune donnée métier : seulement des métadonnées et des estimations de volume.

\echo '== Version'
select version();

\echo '== Paramètres utiles au décodage logique'
select name, setting, unit
from pg_settings
where name in ('wal_level', 'max_replication_slots', 'max_wal_senders', 'max_slot_wal_keep_size',
               'wal_keep_size', 'hot_standby_feedback', 'server_version')
order by name;

\echo '== Tables du schéma : clé primaire, replica identity, volume estimé'
select c.relname                                        as table_name,
       case c.relreplident when 'd' then 'DEFAULT' when 'f' then 'FULL'
                           when 'i' then 'INDEX'   when 'n' then 'NOTHING' end as replica_identity,
       (select string_agg(a.attname, ',' order by array_position(i.indkey::int2[], a.attnum))
          from pg_index i
          join pg_attribute a on a.attrelid = i.indrelid and a.attnum = any (i.indkey)
         where i.indrelid = c.oid and i.indisprimary)   as primary_key,
       c.reltuples::bigint                              as estimated_rows,
       pg_size_pretty(pg_total_relation_size(c.oid))    as total_size
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = :'schema' and c.relkind in ('r', 'p')
order by c.relname;

\echo '== Colonnes : type, nullabilité, défaut'
select c.table_name, c.ordinal_position, c.column_name, c.data_type, c.udt_name,
       c.character_maximum_length, c.numeric_precision, c.numeric_scale, c.is_nullable, c.column_default
from information_schema.columns c
where c.table_schema = :'schema'
order by c.table_name, c.ordinal_position;

\echo '== Types non standard (domaines, types de compatibilité, types utilisateur)'
select c.table_name, c.column_name, c.data_type, c.udt_schema, c.udt_name, c.domain_name
from information_schema.columns c
where c.table_schema = :'schema'
  and (c.domain_name is not null or c.data_type = 'USER-DEFINED' or c.udt_schema not in ('pg_catalog'))
order by c.table_name, c.column_name;

\echo '== Publications et tables publiées'
select p.pubname, p.puballtables, p.pubinsert, p.pubupdate, p.pubdelete, p.pubtruncate,
       pt.schemaname, pt.tablename
from pg_publication p
left join pg_publication_tables pt on pt.pubname = p.pubname
order by p.pubname, pt.schemaname, pt.tablename;

\echo '== Slots de réplication existants'
select slot_name, plugin, slot_type, database, active, wal_status, safe_wal_size,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) as wal_retenu
from pg_replication_slots;
-- Sur un serveur de secours, remplacer pg_current_wal_lsn() par pg_last_wal_replay_lsn().
