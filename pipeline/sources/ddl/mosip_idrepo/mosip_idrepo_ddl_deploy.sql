-- Copie de référence du DDL officiel MOSIP, sans modification.
-- Source : https://github.com/mosip/id-repository/blob/v1.1.5/db_scripts/mosip_idrepo/mosip_idrepo_ddl_deploy.sql
-- Dépôt mosip/id-repository, tag v1.1.5, copié le 16/10/2026. Licence MPL-2.0 (dépôt MOSIP).
-- Référencé par docs/datamart.md. Vérifier l'instance réelle (\d+) : elle peut différer après mise à jour.

\c mosip_idrepo sysadmin

\ir ddl/idrepo-uin.sql
\ir ddl/idrepo-uin_h.sql
\ir ddl/idrepo-uin_document.sql
\ir ddl/idrepo-uin_document_h.sql
\ir ddl/idrepo-uin_biometric.sql
\ir ddl/idrepo-uin_biometric_h.sql
\ir ddl/idrepo-uin_hash_salt.sql
\ir ddl/idrepo-uin_encrypt_salt.sql
\ir ddl/idrepo-uin_auth_lock.sql

\ir ddl/idrepo-fk.sql
