-- Exemple de structures du Data Mart pour le pipeline CDC (PostgreSQL 14+).
-- À découper en migrations ADDITIVES dans l'outil de migration du Data Mart (Flyway dans ce dépôt) ;
-- ne jamais l'exécuter tel quel en production. Les colonnes d'état viennent du DDL MOSIP v1.1.5
-- (references/mosip-115.md) et doivent rester alignées sur column.include.list du connecteur.

create schema if not exists etat;
create schema if not exists pipeline;
create schema if not exists bi;

-- ---------------------------------------------------------------------------------------------------
-- Registre des lots : garantit qu'un lot Spark rejoué n'est appliqué qu'une fois.
-- « requete » contient la génération de checkpoint (ex. etat_regprc@g1).
-- ---------------------------------------------------------------------------------------------------
create table if not exists pipeline.lot_traite (
    requete          text        not null,
    lot_id           bigint      not null,
    traite_le        timestamptz not null default now(),
    nb_upserts       int         not null default 0,
    nb_suppressions  int         not null default 0,
    nb_ignores       int         not null default 0,
    nb_rejets        int         not null default 0,
    primary key (requete, lot_id)
);

-- Événements rejetés : coordonnées Kafka et empreinte, jamais le contenu du message.
create table if not exists pipeline.evenement_rejete (
    id            bigint generated always as identity primary key,
    requete       text        not null,
    lot_id        bigint      not null,
    topic         text        not null,
    partition     int         not null,
    kafka_offset  bigint      not null,
    motif         text        not null,
    empreinte     text,
    rejete_le     timestamptz not null default now(),
    unique (topic, partition, kafka_offset)
);

-- Résultats des contrôles qualité.
create table if not exists pipeline.controle_qualite (
    id          bigint generated always as identity primary key,
    controle    text        not null,
    execute_le  timestamptz not null default now(),
    statut      text        not null check (statut in ('ok', 'alerte', 'echec')),
    valeur      numeric,
    seuil       numeric,
    detail      text
);

-- Regroupement des statuts MOSIP, validé par l'équipe MOSIP. AUCUNE valeur fournie ici :
-- relever les codes réels sur l'instance (select status_code, count(*) ... group by 1) et les faire valider.
create table if not exists pipeline.correspondance_statut (
    status_code      text primary key,
    statut_regroupe  text not null check (statut_regroupe in ('abouti', 'rejete', 'echoue', 'en_cours')),
    valide_par       text,
    valide_le        date
);

-- ---------------------------------------------------------------------------------------------------
-- État courant de regprc.registration (une ligne par inscription, clé pseudonymisée).
-- ---------------------------------------------------------------------------------------------------
create table if not exists etat.registration (
    rid_empreinte           text primary key,      -- HMAC-SHA-256 du RID, calculé par le job (clé secrète)
    code_centre             text,                  -- dérivé du RID (convention MOSIP à vérifier sur l'instance)
    reg_type                text,
    status_code             text,
    latest_trn_type_code    text,
    latest_trn_status_code  text,
    latest_trn_dtimes       timestamp,
    reg_stage_name          text,
    pkt_cr_dtimes           timestamp,
    is_active               boolean,
    cr_dtimes               timestamp,
    upd_dtimes              timestamp,
    is_deleted              boolean,
    _lsn                    bigint      not null,
    _supprime               boolean     not null default false,
    _source_ts              timestamptz,
    _maj_pipeline           timestamptz not null default now()
);
create index if not exists registration_centre_jour_idx on etat.registration (code_centre, cr_dtimes);

-- ---------------------------------------------------------------------------------------------------
-- Fait d'enrôlement, grain jour × centre × type d'opération × statut regroupé.
-- Sexe et tranche d'âge : pas de source anonyme en MOSIP 1.1.5 (references/mosip-115.md § 3).
-- Règle de date à valider : cr_dtimes (réception MOSIP) ou pkt_cr_dtimes (création au centre).
-- ---------------------------------------------------------------------------------------------------
create table if not exists bi.fait_enrolement (
    jour            date not null,
    code_centre     text not null,
    type_operation  text not null,
    statut          text not null,
    inscriptions    int  not null check (inscriptions >= 0),
    primary key (jour, code_centre, type_operation, statut)
);

-- Recalcule les cases (jour, centre) touchées à partir de l'état courant. Idempotent : rejouer donne le même
-- résultat. Appelé dans la transaction du lot, après les upserts.
create or replace function bi.recalculer_enrolement(p_jours date[], p_centres text[])
returns void
language sql
as $$
    delete from bi.fait_enrolement f
    using unnest(p_jours, p_centres) as t(jour, code_centre)
    where f.jour = t.jour and f.code_centre = t.code_centre;

    insert into bi.fait_enrolement (jour, code_centre, type_operation, statut, inscriptions)
    select r.cr_dtimes::date,
           coalesce(r.code_centre, 'inconnu'),
           coalesce(r.reg_type, 'inconnu'),
           coalesce(c.statut_regroupe, 'non_classe'),
           count(*)
    from etat.registration r
    join (select distinct jour, code_centre from unnest(p_jours, p_centres) as u(jour, code_centre)) t
      on r.cr_dtimes::date = t.jour and coalesce(r.code_centre, 'inconnu') = t.code_centre
    left join pipeline.correspondance_statut c on c.status_code = r.status_code
    where not r._supprime
      and r.cr_dtimes is not null
    group by 1, 2, 3, 4;
$$;

-- Fraîcheur lue par l'API (même définition que la table du dépôt ; ne pas la recréer si elle existe).
create table if not exists bi.source_fraicheur (
    source              text primary key,
    libelle             text not null,
    ordre               int  not null,
    premiere_donnee     date,
    derniere_donnee     timestamptz,
    dernier_chargement  timestamptz
);

-- Rôles (exemple) : le pipeline écrit, l'API lit bi seulement.
-- grant usage on schema etat, pipeline, bi to <role_pipeline>;
-- grant select, insert, update on all tables in schema etat, pipeline to <role_pipeline>;
-- grant select, insert, update, delete on bi.fait_enrolement to <role_pipeline>;
-- grant select, insert, update on bi.source_fraicheur to <role_pipeline>;
-- grant execute on function bi.recalculer_enrolement(date[], text[]) to <role_pipeline>;
-- grant usage on schema bi to <role_api>;  grant select on all tables in schema bi to <role_api>;
