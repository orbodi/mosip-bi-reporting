-- Base MOSIP SIMULÉE (développement uniquement) : reproduit la base mosip_regprc pour la seule table
-- regprc.registration, avec le DDL officiel v1.1.5 (fichier 02, monté depuis pipeline/sources/ddl/).
-- Repris du script officiel mosip_regprc_db.sql (tag v1.1.5) : schéma regprc, propriétaire sysadmin.
create schema regprc;
alter schema regprc owner to sysadmin;
alter database mosip_regprc set search_path to regprc, pg_catalog, public;
set search_path to regprc, pg_catalog, public;
