-- Prérequis du connecteur Debezium sur la base MOSIP SIMULÉE (développement).
-- En recette et en production, ces commandes sont faites par le DBA après validation, une par une
-- (voir le skill mosip-bi-pipeline, assets/prerequis-postgres.example.sql). wal_level=logical et
-- max_slot_wal_keep_size sont passés au démarrage du conteneur (deploy/docker-compose.yml).

-- Rôle dédié, sans superutilisateur ; mot de passe lu dans l'environnement du conteneur, jamais écrit ici.
\getenv mot_de_passe_cdc MOSIP_CDC_MOT_DE_PASSE
create role bi_cdc with login replication password :'mot_de_passe_cdc';
grant connect on database mosip_regprc to bi_cdc;
grant usage on schema regprc to bi_cdc;
-- Lecture de la seule table capturée (le snapshot initial la lit).
grant select on regprc.registration to bi_cdc;

-- Publication explicite, créée par le propriétaire de la table (publication.autocreate.mode=disabled côté connecteur).
create publication bi_cdc_regprc for table regprc.registration;
