-- Pipeline temps réel de l'enrôlement (décision du 16/10/2026 dans docs/decisions.md, skill mosip-bi-pipeline).
-- MOSIP (regprc.registration) → Debezium → Kafka → job PySpark → schémas etat et pipeline → bi.fait_enrolement_jour.
-- Migration additive : nouveaux schémas et tables, nouvelle colonne, contrainte de somme élargie, fonctions.
-- Les colonnes de etat.registration viennent du DDL officiel MOSIP v1.1.5
-- (pipeline/sources/ddl/mosip_regprc/regprc-registration.sql) et suivent column.include.list du connecteur
-- (pipeline/cdc/connecteurs/). Le RID n'y figure jamais : seulement son empreinte HMAC et le code centre dérivé.

create schema if not exists etat;
create schema if not exists pipeline;

-- ---------------------------------------------------------------------------------------------------------------
-- Registre des lots : un lot Spark rejoué n'est appliqué qu'une fois (écrit dans la même transaction que le lot).
-- « requete » porte la génération de checkpoint (ex. etat_regprc@g1) : un nouveau checkpoint repart à lot_id 0.
-- ---------------------------------------------------------------------------------------------------------------
create table pipeline.lot_traite (
    requete          text        not null,
    lot_id           bigint      not null,
    traite_le        timestamptz not null default now(),
    nb_upserts       int         not null default 0,
    nb_suppressions  int         not null default 0,
    nb_ignores       int         not null default 0,
    nb_rejets        int         not null default 0,
    primary key (requete, lot_id)
);
comment on table pipeline.lot_traite is 'Lots appliqués par les jobs de streaming (idempotence des rejeux).';

-- Événements illisibles : coordonnées Kafka et empreinte, jamais le contenu du message (données personnelles).
create table pipeline.evenement_rejete (
    id            bigint      generated always as identity primary key,
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

create table pipeline.controle_qualite (
    id          bigint      generated always as identity primary key,
    controle    text        not null,
    execute_le  timestamptz not null default now(),
    statut      text        not null check (statut in ('ok', 'alerte', 'echec')),
    valeur      numeric,
    seuil       numeric,
    detail      text
);

-- Regroupement des statuts MOSIP. AUCUNE valeur ici : la correspondance se fait valider par l'équipe MOSIP à partir
-- des codes relevés sur l'instance. Tant qu'un code n'y figure pas, ses inscriptions comptent en « non classées ».
-- (Le profil dev en charge une version de démonstration : db/dev/R__donnees_dev.sql.)
create table pipeline.correspondance_statut (
    status_code      text primary key,
    statut_regroupe  text not null check (statut_regroupe in ('abouti', 'rejete', 'echoue', 'en_cours')),
    valide_par       text,
    valide_le        date,
    commentaire      text
);
comment on table pipeline.correspondance_statut is
    'registration.status_code → statut affiché (abouti = NIU générés). Validée par l''équipe MOSIP ; vide sinon.';

-- ---------------------------------------------------------------------------------------------------------------
-- État courant de regprc.registration : une ligne par inscription, écrite par le job etat_regprc.
-- ---------------------------------------------------------------------------------------------------------------
create table etat.registration (
    rid_empreinte           text        primary key,
    code_centre             text,
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
create index registration_jour_centre_idx on etat.registration ((cr_dtimes::date), code_centre);
comment on column etat.registration.rid_empreinte is 'HMAC-SHA-256 du RID (clé secrète du pipeline). Jamais le RID.';
comment on column etat.registration.code_centre is 'Cinq premiers chiffres du RID (convention MOSIP, à vérifier).';
comment on column etat.registration._lsn is 'LSN du dernier événement appliqué : garde contre les rejeux.';
comment on column etat.registration._supprime is 'Suppression reçue de MOSIP (op d) : ligne conservée, exclue.';

-- ---------------------------------------------------------------------------------------------------------------
-- Fait d'enrôlement : statuts sans correspondance validée comptés à part, jamais devinés.
-- ---------------------------------------------------------------------------------------------------------------
alter table bi.fait_enrolement_jour add column non_classees int not null default 0;
-- Contrainte de V1 remplacée par une contrainte plus large (aucune donnée modifiée).
alter table bi.fait_enrolement_jour drop constraint fait_enrolement_jour_check;
alter table bi.fait_enrolement_jour add constraint fait_enrolement_jour_somme_statuts
    check (niu_generes + rejetees + echouees + en_cours + non_classees = inscriptions);
comment on column bi.fait_enrolement_jour.niu_generes is
    'Inscriptions abouties (statut regroupé « abouti »), tous types de demande. NIU générés = type NEW.';
comment on column bi.fait_enrolement_jour.non_classees is
    'Inscriptions dont le status_code n''a pas de correspondance validée (pipeline.correspondance_statut).';
comment on table bi.fait_enrolement_jour is
    'Inscriptions par jour de réception (cr_dtimes, règle à confirmer), centre et profil. Recalculé depuis '
    'etat.registration par bi.recalculer_enrolement_jour (pipeline temps réel).';

-- Centre absent du référentiel : ses inscriptions restent visibles sous « Centre non référencé ».
insert into bi.zone (niveau, code, nom, parent_id, ordre)
values ('region', 'HORS_REFERENTIEL', 'Hors référentiel', null, 99)
on conflict (code) do nothing;
insert into bi.zone (niveau, code, nom, parent_id, ordre)
select 'centre', 'CENTRE_NON_REFERENCE', 'Centre non référencé', id, 0
from bi.zone
where code = 'HORS_REFERENTIEL'
on conflict (code) do nothing;

-- ---------------------------------------------------------------------------------------------------------------
-- Recalcul des cases (jour, centre) touchées par un lot, à partir de l'état courant. Idempotent : le rejouer donne
-- le même résultat. Appelé par le job dans la transaction du lot, avec les cases d'avant ET d'après la mise à jour.
-- Règles (docs/indicateurs.md, à confirmer) : jour = cr_dtimes ; exclues : suppressions reçues et is_deleted.
-- ---------------------------------------------------------------------------------------------------------------
create function bi.recalculer_enrolement_jour(p_jours date[], p_centres text[])
returns void
language sql
as $$
    with hors_ref as (
        select id from bi.zone where code = 'CENTRE_NON_REFERENCE'
    ),
    cases as (
        select distinct t.jour, coalesce(z.id, (select id from hors_ref)) as centre_id
        from unnest(p_jours, p_centres) as t(jour, code_centre)
        left join bi.zone z on z.niveau = 'centre' and z.code = t.code_centre
    )
    delete from bi.fait_enrolement_jour f
    using cases c
    where f.jour = c.jour and f.centre_id = c.centre_id;

    with hors_ref as (
        select id from bi.zone where code = 'CENTRE_NON_REFERENCE'
    ),
    cases as (
        select distinct t.jour, coalesce(z.id, (select id from hors_ref)) as centre_id
        from unnest(p_jours, p_centres) as t(jour, code_centre)
        left join bi.zone z on z.niveau = 'centre' and z.code = t.code_centre
    ),
    inscriptions as (
        select r.cr_dtimes::date                       as jour,
               coalesce(z.id, (select id from hors_ref)) as centre_id,
               coalesce(r.reg_type, 'inconnu')         as type_demande,
               c.statut_regroupe                       as statut
        from etat.registration r
        left join bi.zone z on z.niveau = 'centre' and z.code = r.code_centre
        left join pipeline.correspondance_statut c on c.status_code = r.status_code
        where not r._supprime
          and not coalesce(r.is_deleted, false)
          and r.cr_dtimes is not null
          and r.cr_dtimes::date = any (p_jours)
    )
    insert into bi.fait_enrolement_jour (jour, centre_id, sexe, tranche_age, type_demande, inscriptions,
                                         niu_generes, en_cours, echouees, rejetees, non_classees)
    select i.jour, i.centre_id, 'I', 'inconnu', i.type_demande,
           count(*),
           count(*) filter (where i.statut = 'abouti'),
           count(*) filter (where i.statut = 'en_cours'),
           count(*) filter (where i.statut = 'echoue'),
           count(*) filter (where i.statut = 'rejete'),
           count(*) filter (where i.statut is null)
    from inscriptions i
    join cases c on c.jour = i.jour and c.centre_id = i.centre_id
    group by i.jour, i.centre_id, i.type_demande;
$$;
comment on function bi.recalculer_enrolement_jour(date[], text[]) is
    'Recalcule bi.fait_enrolement_jour pour les couples (jour, code centre) donnés, depuis etat.registration.';

-- Recalcul complet (après un changement du référentiel des centres ou de la correspondance des statuts, ou pour un
-- contrôle de dérive). Ne touche que le fait dérivé, jamais l'état courant. À lancer volontairement.
create function bi.recalculer_enrolement_tout()
returns void
language sql
as $$
    select bi.recalculer_enrolement_jour(array_agg(jour), array_agg(code_centre))
    from (
        select distinct cr_dtimes::date as jour, coalesce(code_centre, 'inconnu') as code_centre
        from etat.registration
        where cr_dtimes is not null
        union
        select f.jour, z.code
        from bi.fait_enrolement_jour f
        join bi.zone z on z.id = f.centre_id
    ) cases;
$$;

-- Contrôles de qualité : concordance état courant ↔ faits, et inscriptions non classées. Résultat consigné dans
-- pipeline.controle_qualite. À appeler périodiquement (ou par l'outil de vérification de pipeline/outils).
create function pipeline.controler_enrolement()
returns table (controle text, statut text, valeur numeric, detail text)
language plpgsql
as $$
declare
    v_etat  bigint;
    v_fait  bigint;
    v_nc    bigint;
begin
    select count(*) into v_etat
    from etat.registration
    where not _supprime and not coalesce(is_deleted, false) and cr_dtimes is not null;

    select coalesce(sum(f.inscriptions), 0), coalesce(sum(f.non_classees), 0) into v_fait, v_nc
    from bi.fait_enrolement_jour f;

    insert into pipeline.controle_qualite (controle, statut, valeur, seuil, detail)
    values ('enrolement_etat_egal_faits', case when v_etat = v_fait then 'ok' else 'echec' end, v_fait - v_etat, 0,
            format('état courant %s, faits %s', v_etat, v_fait)),
           ('enrolement_non_classees', case when v_nc = 0 then 'ok' else 'alerte' end, v_nc, 0,
            'inscriptions dont le status_code n''a pas de correspondance validée');

    return query
        select q.controle, q.statut, q.valeur, q.detail
        from pipeline.controle_qualite q
        order by q.id desc
        limit 2;
end;
$$;

-- Rôles en recette et en production (exemple ; en développement, « bi » fait tout) :
--   pipeline : usage sur etat, pipeline, bi ; select/insert/update sur etat.* et pipeline.* ;
--              select/insert/delete sur bi.fait_enrolement_jour ; insert/update sur bi.source_fraicheur ;
--              execute sur bi.recalculer_enrolement_jour.
--   api      : usage sur bi ; select sur les tables de bi seulement (jamais etat ni pipeline).
