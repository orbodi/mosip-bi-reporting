-- Copie de référence du DDL officiel MOSIP, sans modification.
-- Source : https://github.com/mosip/registration/blob/v1.1.5/db_scripts/mosip_regprc/mosip_regprc_ddl_deploy.sql
-- Dépôt mosip/registration, tag v1.1.5, copié le 16/10/2026. Licence MPL-2.0 (dépôt MOSIP).
-- Référencé par docs/datamart.md. Vérifier l'instance réelle (\d+) : elle peut différer après mise à jour.

\c mosip_regprc sysadmin

\ir ddl/regprc-individual_demographic_dedup.sql
\ir ddl/regprc-registration.sql
\ir ddl/regprc-registration_list.sql
\ir ddl/regprc-registration_transaction.sql

\ir ddl/regprc-reg_manual_verification.sql
\ir ddl/regprc-transaction_type.sql
\ir ddl/regprc-rid_seq.sql
\ir ddl/regprc-reg_bio_ref.sql
\ir ddl/regprc-reg_demo_dedupe_list.sql
\ir ddl/regprc-abis_application.sql
\ir ddl/regprc-abis_request.sql
\ir ddl/regprc-abis_response.sql
\ir ddl/regprc-abis_response_det.sql

\ir ddl/regprc-reg_lost_uin_det.sql

\ir ddl/regprc-fk.sql
