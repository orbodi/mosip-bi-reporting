-- Copie de référence du DDL officiel MOSIP, sans modification.
-- Source : https://github.com/mosip/partner-management-services/blob/v1.1.5/db_scripts/mosip_pms/mosip_pms_ddl_deploy.sql
-- Dépôt mosip/partner-management-services, tag v1.1.5, copié le 16/10/2026. Licence MPL-2.0 (dépôt MOSIP).
-- Référencé par docs/datamart.md. Vérifier l'instance réelle (\d+) : elle peut différer après mise à jour.

\c mosip_pms sysadmin

\ir ddl/pms-misp.sql
\ir ddl/pms-misp_license.sql
\ir ddl/pms-policy_group.sql
\ir ddl/pms-auth_policy.sql
\ir ddl/pms-auth_policy_h.sql
\ir ddl/pms-partner.sql
\ir ddl/pms-partner_policy.sql
\ir ddl/pms-partner_policy_request.sql
\ir ddl/pms-partner_contact.sql
\ir ddl/pms-partner_h.sql
\ir ddl/pms-partner_type.sql
\ir ddl/pms-tspid_seq.sql
\ir ddl/pms-otp_transaction.sql
\ir ddl/pms-partner_policy_bioextract.sql
\ir ddl/pms-partner_policy_credential_type.sql

\ir ddl/pms-fk.sql
