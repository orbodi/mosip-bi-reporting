-- Exécuté une seule fois, à la création du volume (développement).
-- « bi » possède le schéma (migrations Flyway et pipeline) ; « bi_lecture » sert aux outils en lecture seule
-- (serveur MCP « base-bi » de Claude Code, requêtes d'audit).
create role bi_lecture login password 'bi_lecture';
create schema if not exists bi authorization bi;
grant connect on database bi to bi_lecture;
grant usage on schema bi to bi_lecture;
alter default privileges for role bi in schema bi grant select on tables to bi_lecture;
