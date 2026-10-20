-- Prérequis du connecteur bi-cdc-idrepo sur la base mosip_idrepo (préparé par Claude, à faire exécuter par le DBA).
-- Décision du 20/10/2026 (docs/decisions.md) : sexe et âge des NIU lus dans le profil anonymisé de MOSIP,
-- idrepo.anonymous_profile (MOSIP 1.1.5.5 et plus). Aucune autre table de mosip_idrepo n'est capturée : uin, uin_h,
-- documents et biométrie restent interdits.
-- Partie A : contrôles en lecture, sans effet. Partie B : commandes commentées, à exécuter une par une après
-- validation explicite de chacune. Aucune n'est destructive ; aucun mot de passe ne figure ici.

-- =====================================================================================================
-- A. Contrôles (lecture seule)
-- =====================================================================================================
-- A1. La table existe-t-elle ? (absente en MOSIP 1.1.5 : la version de l'instance doit être 1.1.5.5 ou plus)
select to_regclass('idrepo.anonymous_profile') as table_presente;

-- A2. Colonnes réelles (comparer à pipeline/sources/ddl/mosip_idrepo/idrepo-anonymous_profile.sql).
select column_name, data_type, is_nullable
from information_schema.columns
where table_schema = 'idrepo' and table_name = 'anonymous_profile'
order by ordinal_position;

-- A3. Clé primaire et replica identity.
select c.relreplident as replica_identity,
       exists (select 1 from pg_index i where i.indrelid = c.oid and i.indisprimary) as has_primary_key
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'idrepo' and c.relname = 'anonymous_profile';

-- A4. Valeurs à faire valider (pipeline.correspondance_sexe) et contrôles de remplissage. Comptages seuls, aucun
--     profil affiché. Si « profile » est de type jsonb, retirer les « ::jsonb ».
select p.profile::jsonb ->> 'processName' as processus,
       p.profile::jsonb -> 'newProfile' ->> 'gender' as genre,
       count(*) as profils,
       count(*) filter (where p.profile::jsonb -> 'newProfile' ->> 'yearOfBirth' is null) as sans_annee,
       count(*) filter (where p.profile::jsonb -> 'newProfile' -> 'location' is null) as sans_lieu
from idrepo.anonymous_profile p
group by 1, 2
order by 3 desc;

-- A5. Forme des lieux (codes de master.location ?) : nombre d'éléments, jamais les valeurs.
select jsonb_typeof(p.profile::jsonb -> 'newProfile' -> 'location') as forme,
       jsonb_array_length(case when jsonb_typeof(p.profile::jsonb -> 'newProfile' -> 'location') = 'array'
                               then p.profile::jsonb -> 'newProfile' -> 'location' end) as elements,
       count(*)
from idrepo.anonymous_profile p
group by 1, 2
order by 3 desc;

-- =====================================================================================================
-- B. Commandes DBA (validation explicite requise, une par une)
-- =====================================================================================================
-- B1. Rôle dédié (le même que pour les autres bases s'il existe déjà), sans superutilisateur.
-- grant connect on database mosip_idrepo to bi_cdc;
-- grant usage on schema idrepo to bi_cdc;
-- grant select (id, profile, cr_dtimes, is_deleted) on idrepo.anonymous_profile to bi_cdc;

-- B2. Publication explicite de la seule table anonymous_profile.
-- create publication bi_cdc_idrepo for table idrepo.anonymous_profile (id, profile, cr_dtimes, is_deleted);
--   (PostgreSQL 15 et plus pour la liste de colonnes ; sinon « for table idrepo.anonymous_profile ».)

-- Retour arrière (connecteur arrêté, après validation) :
-- drop publication bi_cdc_idrepo;  -- le slot bi_cdc_idrepo_<env> se supprime à part (voir le runbook du skill)
