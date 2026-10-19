-- Copie de référence du DDL officiel MOSIP, sans modification.
-- Source : https://github.com/mosip/pre-registration/blob/v1.1.5/db_scripts/mosip_prereg/mosip_prereg_ddl_deploy.sql
-- Dépôt mosip/pre-registration, tag v1.1.5, copié le 16/10/2026. Licence MPL-2.0 (dépôt MOSIP).
-- Référencé par docs/datamart.md. Vérifier l'instance réelle (\d+) : elle peut différer après mise à jour.

\c mosip_prereg sysadmin

\ir ddl/prereg-applicant_demographic.sql
\ir ddl/prereg-applicant_demographic_consumed.sql
\ir ddl/prereg-applicant_document.sql
\ir ddl/prereg-applicant_document_consumed.sql
\ir ddl/prereg-batch_job_execution.sql
\ir ddl/prereg-batch_job_execution_context.sql
\ir ddl/prereg-batch_job_execution_param.sql
\ir ddl/prereg-batch_job_instance.sql
\ir ddl/prereg-batch_step_execution.sql
\ir ddl/prereg-batch_step_execution_context.sql
\ir ddl/prereg-intf_processed_prereg_list.sql
\ir ddl/prereg-pre_registration_transaction.sql
\ir ddl/prereg-processed_prereg_list.sql
\ir ddl/prereg-reg_appointment.sql
\ir ddl/prereg-reg_appointment_consumed.sql
\ir ddl/prereg-reg_available_slot.sql
\ir ddl/prereg-transaction_type.sql
\ir ddl/prereg-language_transliteration.sql
\ir ddl/prereg-prid_seed.sql
\ir ddl/prereg-prid_seq.sql
\ir ddl/prereg-otp_transaction.sql


\ir ddl/prereg-fk.sql
\ir ddl/prereg-batch-fk.sql
