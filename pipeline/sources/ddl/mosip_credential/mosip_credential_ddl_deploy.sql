-- Copie de référence du DDL officiel MOSIP, sans modification.
-- Source : https://github.com/mosip/id-repository/blob/v1.1.5/db_scripts/mosip_credential/mosip_credential_ddl_deploy.sql
-- Dépôt mosip/id-repository, tag v1.1.5, copié le 16/10/2026. Licence MPL-2.0 (dépôt MOSIP).
-- Référencé par docs/datamart.md. Vérifier l'instance réelle (\d+) : elle peut différer après mise à jour.

\c mosip_credential sysadmin

\ir ddl/credential-credential_transaction.sql

\ir ddl/credential-batch_job_execution.sql
\ir ddl/credential-batch_job_execution_context.sql
\ir ddl/credential-batch_job_execution_params.sql
\ir ddl/credential-batch_job_instance.sql
\ir ddl/credential-batch_step_execution.sql
\ir ddl/credential-batch_step_execution_context.sql

\ir ddl/credential-fk.sql