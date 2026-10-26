-- Suivi d'un dossier (I11) : journal des recherches. Une ligne par recherche : quand, qui, résultat. JAMAIS le RID
-- ni son empreinte : le journal dit qu'une recherche a eu lieu, pas sur quel dossier.
-- Sans plafond de recherches (décision du 26/10/2026) ; chaque utilisateur a accès à tout le Togo (25/10/2026).
-- L'API écrit avec api_reader (lecture seule partout ailleurs) : droit d'insertion sur cette seule table.

create table bi.journal_suivi (
    recherche_le  timestamptz not null default now(),
    utilisateur   text        not null,
    resultat      text        not null check (resultat in ('trouve', 'introuvable', 'format'))
);
create index journal_suivi_recherche_le_idx on bi.journal_suivi (recherche_le);
comment on table bi.journal_suivi is
    'Recherches du suivi d''un dossier : quand, qui (identifiant Keycloak, « anonyme » sans Keycloak), résultat ; jamais le RID.';

-- api_reader existe sur la BD de traitement (09_droits_bi.sql), pas dans les bases de test : droit accordé s'il existe.
do $$
begin
    if exists (select 1 from pg_roles where rolname = 'api_reader') then
        grant select, insert on bi.journal_suivi to api_reader;
    end if;
end
$$;
