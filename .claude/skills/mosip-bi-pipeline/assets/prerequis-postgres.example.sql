-- Prérequis du connecteur Debezium sur la base MOSIP (exemple, à adapter).
-- Partie A : contrôles en lecture, sans effet.
-- Partie B : commandes à faire exécuter par le DBA en production APRÈS validation explicite. Elles sont commentées
--            volontairement. Aucune n'est destructive ; aucun mot de passe ne figure ici.
-- Remplacer : <base> (ex. mosip_regprc), <schema> (ex. regprc), <role_debezium>, <publication>, liste des tables.

-- =====================================================================================================
-- A. Contrôles (lecture seule)
-- =====================================================================================================
show wal_level;                       -- attendu : logical
show max_replication_slots;           -- assez pour les slots existants + les nouveaux
show max_wal_senders;
show max_slot_wal_keep_size;          -- -1 = illimité : risque de saturation disque, à borner (PG13+)

-- Tables à capturer : clé primaire et replica identity (DEFAULT suffit si la clé primaire existe)
select n.nspname as schema_name, c.relname as table_name,
       c.relreplident as replica_identity,
       exists (select 1 from pg_index i where i.indrelid = c.oid and i.indisprimary) as has_primary_key
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = '<schema>' and c.relname in ('registration');   -- tables envisagées

-- Le rôle existe-t-il déjà ? A-t-il REPLICATION ?
select rolname, rolreplication, rolcanlogin, rolsuper from pg_roles where rolname = '<role_debezium>';

-- Publications et slots existants (ne rien recréer en double)
select * from pg_publication;
select slot_name, plugin, active, wal_status from pg_replication_slots;

-- =====================================================================================================
-- B. Commandes DBA (production : validation explicite requise, une par une)
-- =====================================================================================================
-- B1. Paramètres (postgresql.conf ou ALTER SYSTEM ; wal_level demande un redémarrage planifié)
-- alter system set wal_level = 'logical';
-- alter system set max_slot_wal_keep_size = '50GB';   -- à dimensionner selon l'espace disque
-- (puis pg_hba.conf : ligne pour la BASE <base>, le rôle <role_debezium> et l'hôte Kafka Connect, par ex.
--    hostssl  <base>  <role_debezium>  <ip_kafka_connect>/32  scram-sha-256
--  le mot-clé « replication » ne couvre que la réplication physique, pas la réplication logique)

-- B2. Rôle dédié, sans superutilisateur. Mot de passe défini hors script (\password ou coffre).
-- create role <role_debezium> with replication login;
-- grant connect on database <base> to <role_debezium>;
-- grant create on database <base> to <role_debezium>;  -- seulement si Debezium crée la publication : NE PAS accorder
--                                                        -- avec publication.autocreate.mode=disabled (à confirmer en recette)
-- grant usage on schema <schema> to <role_debezium>;
-- grant select on <schema>.registration to <role_debezium>;   -- uniquement les tables capturées ; en ajouter une
--                                                            -- seulement si un indicateur validé l'exige

-- B3. Publication explicite (par le propriétaire des tables ou le DBA). Pas de FOR ALL TABLES.
-- create publication <publication> for table <schema>.registration;

-- B4. SEULEMENT si une dérogation écrite (docs/decisions.md) autorise une écriture dans la base MOSIP :
--     schéma technique pour heartbeat et signaux (snapshots incrémentaux). Sans dérogation, ne rien créer ici.
-- create schema bi_cdc authorization <role_debezium>;
-- create table bi_cdc.heartbeat (id int primary key, ts timestamptz not null);
-- create table bi_cdc.debezium_signal (id varchar(64) primary key, type varchar(32) not null, data varchar(2048));
-- alter publication <publication> add table bi_cdc.heartbeat, bi_cdc.debezium_signal;

-- Retour arrière (uniquement connecteur arrêté et après validation) :
-- drop publication <publication>;  -- et, à part, pg_drop_replication_slot('<slot>') : voir references/exploitation.md
