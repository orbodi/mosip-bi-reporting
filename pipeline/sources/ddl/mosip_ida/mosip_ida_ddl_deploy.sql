-- Copie de référence du DDL officiel MOSIP, sans modification.
-- Source : https://github.com/mosip/id-authentication/blob/v1.1.5/db_scripts/mosip_ida/mosip_ida_ddl_deploy.sql
-- Dépôt mosip/id-authentication, tag v1.1.5, copié le 16/10/2026. Licence MPL-2.0 (dépôt MOSIP).
-- Référencé par docs/datamart.md. Vérifier l'instance réelle (\d+) : elle peut différer après mise à jour.

\c mosip_ida sysadmin

\ir ddl/ida-auth_transaction.sql
\ir ddl/ida-uin_auth_lock.sql
\ir ddl/ida-uin_hash_salt.sql
\ir ddl/ida-key_alias.sql
\ir ddl/ida-key_store.sql
\ir ddl/ida-key_policy_def.sql
\ir ddl/ida-key_policy_def_h.sql
\ir ddl/ida-identity_cache.sql
\ir ddl/ida-data_encrypt_keystore.sql
\ir ddl/ida-otp_transaction.sql
\ir ddl/ida-ca_cert_store.sql
\ir ddl/ida-credential_event_store.sql
\ir ddl/ida-hotlist_cache.sql


\ir ddl/ida-batch_job_execution.sql
\ir ddl/ida-batch_job_execution_context.sql
\ir ddl/ida-batch_job_execution_params.sql
\ir ddl/ida-batch_job_instance.sql
\ir ddl/ida-batch_step_execution.sql
\ir ddl/ida-batch_step_execution_context.sql

\ir ddl/ida-fk.sql

