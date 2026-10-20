-- Pré-inscriptions et NIU générés par sexe et tranche d'âge (décisions du 20/10/2026 dans docs/decisions.md).
-- Migration additive : nouvelles tables et fonctions, aucune donnée existante modifiée.
--
-- 1. Pré-inscriptions : prereg.applicant_demographic et prereg.applicant_demographic_consumed, colonnes sans identité
--    seulement (prereg_id en empreinte HMAC, status_code, cr_dtimes, upd_dtimes ; DDL officiels v1.1.5 copiés dans
--    pipeline/sources/ddl/mosip_prereg/). demog_detail, demog_detail_hash et cr_appuser_id ne sont jamais capturés.
-- 2. Profil des NIU : idrepo.anonymous_profile (MOSIP 1.1.5.5 et plus, profil anonymisé publié par MOSIP). Le profil
--    JSON n'est jamais écrit : le job en tire le processus, le jour, le genre, la tranche d'âge (l'année de naissance
--    n'est pas conservée) et la région, résolue à l'écriture depuis bi.zone (les codes de lieux ne sont pas conservés).

-- ---------------------------------------------------------------------------------------------------------------
-- 1. Pré-inscriptions
-- ---------------------------------------------------------------------------------------------------------------

-- Regroupement des statuts de pré-inscription. AUCUNE valeur ici : la correspondance se fait valider par l'équipe
-- MOSIP. Tant qu'un code n'y figure pas, ses demandes comptent en « non classées ». (Le profil dev en charge une
-- version de démonstration : db/dev/R__donnees_dev.sql.)
create table pipeline.correspondance_statut_preinscription (
    status_code      text primary key,
    statut_regroupe  text not null check (statut_regroupe in ('en_attente', 'reservee', 'expiree', 'annulee')),
    valide_par       text,
    valide_le        date,
    commentaire      text
);
comment on table pipeline.correspondance_statut_preinscription is
    'prereg.applicant_demographic.status_code → statut affiché. Validée par l''équipe MOSIP ; vide sinon.';

-- État courant : une ligne par pré-inscription et par table MOSIP (une demande consommée passe de la table active à
-- la table _consumed ; les deux lignes sont gardées, la table _consumed prévaut au recalcul).
create table etat.preinscription (
    prereg_empreinte  text        not null,
    table_source      text        not null check (table_source in ('demande', 'consommee')),
    status_code       text,
    cr_dtimes         timestamp,
    upd_dtimes        timestamp,
    _lsn              bigint      not null,
    _supprime         boolean     not null default false,
    _source_ts        timestamptz,
    _maj_pipeline     timestamptz not null default now(),
    primary key (prereg_empreinte, table_source)
);
create index preinscription_jour_idx on etat.preinscription ((cr_dtimes::date));
comment on column etat.preinscription.prereg_empreinte is 'HMAC-SHA-256 du prereg_id (clé secrète du pipeline).';
comment on column etat.preinscription.table_source is
    'demande = prereg.applicant_demographic ; consommee = prereg.applicant_demographic_consumed.';

-- Fait : demandes par jour de création et statut regroupé (national : une demande n'a pas de centre).
create table bi.fait_preinscription_jour (
    jour       date not null,
    statut     text not null check (statut in ('en_attente', 'reservee', 'expiree', 'annulee', 'non_classe')),
    demandes   int  not null check (demandes >= 0),
    consommees int  not null check (consommees >= 0 and consommees <= demandes),
    primary key (jour, statut)
);
comment on table bi.fait_preinscription_jour is
    'Pré-inscriptions par jour de création (cr_dtimes) et statut regroupé. Recalculé depuis etat.preinscription.';
comment on column bi.fait_preinscription_jour.consommees is
    'Demandes reprises lors d''une inscription en centre (table _consumed) : « Honorées à l''inscription ».';

-- Recalcul des jours touchés par un lot, depuis l'état courant. Idempotent. Une demande compte une fois : sa ligne
-- _consumed si elle existe, sinon sa ligne active ; une ligne supprimée de MOSIP ne compte pas.
create function bi.recalculer_preinscription_jour(p_jours date[])
returns void
language sql
as $$
    delete from bi.fait_preinscription_jour where jour = any (p_jours);

    with candidates as (
        select distinct prereg_empreinte
        from etat.preinscription
        where cr_dtimes::date = any (p_jours)
    ),
    demandes as (
        select distinct on (p.prereg_empreinte)
               p.prereg_empreinte, p.status_code, p.cr_dtimes, p.table_source = 'consommee' as consommee
        from etat.preinscription p
        join candidates c on c.prereg_empreinte = p.prereg_empreinte
        where not p._supprime and p.cr_dtimes is not null
        order by p.prereg_empreinte, (p.table_source = 'consommee') desc
    )
    insert into bi.fait_preinscription_jour (jour, statut, demandes, consommees)
    select d.cr_dtimes::date,
           coalesce(c.statut_regroupe, 'non_classe'),
           count(*),
           count(*) filter (where d.consommee)
    from demandes d
    left join pipeline.correspondance_statut_preinscription c on c.status_code = d.status_code
    where d.cr_dtimes::date = any (p_jours)
    group by 1, 2;
$$;
comment on function bi.recalculer_preinscription_jour(date[]) is
    'Recalcule bi.fait_preinscription_jour pour les jours donnés, depuis etat.preinscription.';

-- Recalcul complet (après un changement de la correspondance des statuts, ou pour un contrôle de dérive).
create function bi.recalculer_preinscription_tout()
returns void
language sql
as $$
    select bi.recalculer_preinscription_jour(array_agg(jour))
    from (
        select distinct cr_dtimes::date as jour from etat.preinscription where cr_dtimes is not null
        union
        select jour from bi.fait_preinscription_jour
    ) j;
$$;

-- Contrôles : concordance état courant ↔ faits, demandes non classées.
create function pipeline.controler_preinscription()
returns table (controle text, statut text, valeur numeric, detail text)
language plpgsql
as $$
declare
    v_etat  bigint;
    v_fait  bigint;
    v_nc    bigint;
begin
    select count(distinct p.prereg_empreinte) into v_etat
    from etat.preinscription p
    where not p._supprime and p.cr_dtimes is not null;

    select coalesce(sum(f.demandes), 0), coalesce(sum(f.demandes) filter (where f.statut = 'non_classe'), 0)
    into v_fait, v_nc
    from bi.fait_preinscription_jour f;

    insert into pipeline.controle_qualite (controle, statut, valeur, seuil, detail)
    values ('preinscription_etat_egal_faits', case when v_etat = v_fait then 'ok' else 'echec' end, v_fait - v_etat,
            0, format('état courant %s, faits %s', v_etat, v_fait)),
           ('preinscription_non_classees', case when v_nc = 0 then 'ok' else 'alerte' end, v_nc, 0,
            'pré-inscriptions dont le status_code n''a pas de correspondance validée');

    return query
        select q.controle, q.statut, q.valeur, q.detail
        from pipeline.controle_qualite q
        order by q.id desc
        limit 2;
end;
$$;

-- ---------------------------------------------------------------------------------------------------------------
-- 2. Profil des NIU (idrepo.anonymous_profile)
-- ---------------------------------------------------------------------------------------------------------------

-- Genre du profil MOSIP → sexe affiché. Vide hors développement tant que l'équipe MOSIP ne l'a pas validée : un genre
-- absent compte en « I » (inconnu), jamais deviné.
create table pipeline.correspondance_sexe (
    genre        text primary key,
    sexe         text not null check (sexe in ('F', 'H')),
    valide_par   text,
    valide_le    date,
    commentaire  text
);
comment on table pipeline.correspondance_sexe is
    'Valeur « gender » du profil anonymisé MOSIP → F ou H. Validée par l''équipe MOSIP ; vide sinon.';

-- Région d'une liste de codes de lieux (n'importe quel niveau de bi.zone) : null si aucun code n'est connu ou si les
-- codes désignent plusieurs régions. Utilisée à l'écriture : les codes eux-mêmes ne sont pas conservés.
create function bi.region_des_lieux(p_codes text[])
returns text
language sql
stable
as $$
    with recursive montee as (
        select z.id, z.parent_id, z.code, z.niveau
        from bi.zone z
        where z.code = any (p_codes)
        union
        select p.id, p.parent_id, p.code, p.niveau
        from bi.zone p
        join montee m on p.id = m.parent_id
    )
    select case when count(distinct code) = 1 then min(code) end
    from montee
    where niveau = 'region' and code <> 'HORS_REFERENTIEL';
$$;

-- État courant : une ligne par profil (processus New, Update, Lost).
create table etat.profil_anonyme (
    profil_empreinte  text        primary key,
    processus         text,
    jour              date,
    genre             text,
    tranche_age       text        check (tranche_age in ('0-5', '6-14', '15-18', '19-25', '26-35', '36-45', '46-60',
                                                         '60+', 'inconnu')),
    code_region       text,
    cr_dtimes         timestamp,
    is_deleted        boolean,
    _lsn              bigint      not null,
    _supprime         boolean     not null default false,
    _source_ts        timestamptz,
    _maj_pipeline     timestamptz not null default now()
);
create index profil_anonyme_jour_idx on etat.profil_anonyme (jour);
comment on table etat.profil_anonyme is
    'Profils anonymisés MOSIP réduits aux axes du BI. Jamais le JSON, l''année de naissance ni les codes de lieux.';
comment on column etat.profil_anonyme.jour is 'Champ « date » du profil, à défaut le jour de cr_dtimes.';
comment on column etat.profil_anonyme.tranche_age is
    'Âge au jour du profil (année du jour − année de naissance), en tranches de la maquette Enrôlement.';
comment on column etat.profil_anonyme.code_region is 'Région résolue à l''écriture (bi.region_des_lieux).';

-- Fait : NIU générés (profils « New ») par jour, région, sexe et tranche d'âge (lecture flux, jour de génération).
create table bi.fait_niu_profil_jour (
    jour         date   not null,
    zone_id      bigint not null references bi.zone (id),
    sexe         text   not null check (sexe in ('F', 'H', 'I')),
    tranche_age  text   not null check (tranche_age in ('0-5', '6-14', '15-18', '19-25', '26-35', '36-45', '46-60',
                                                        '60+', 'inconnu')),
    niu_generes  int    not null check (niu_generes >= 0),
    primary key (jour, zone_id, sexe, tranche_age)
);
create index fait_niu_profil_jour_zone_idx on bi.fait_niu_profil_jour (zone_id, jour);
comment on table bi.fait_niu_profil_jour is
    'NIU générés par jour, région, sexe et tranche d''âge, depuis idrepo.anonymous_profile (processus New).';
comment on column bi.fait_niu_profil_jour.zone_id is 'Région, ou « Hors référentiel » si le lieu du profil est inconnu.';

create function bi.recalculer_niu_profil_jour(p_jours date[])
returns void
language sql
as $$
    delete from bi.fait_niu_profil_jour where jour = any (p_jours);

    insert into bi.fait_niu_profil_jour (jour, zone_id, sexe, tranche_age, niu_generes)
    select p.jour,
           coalesce(r.id, h.id),
           coalesce(c.sexe, 'I'),
           coalesce(p.tranche_age, 'inconnu'),
           count(*)
    from etat.profil_anonyme p
    cross join (select id from bi.zone where code = 'HORS_REFERENTIEL') h
    left join bi.zone r on r.niveau = 'region' and r.code = p.code_region
    left join pipeline.correspondance_sexe c on c.genre = p.genre
    where not p._supprime
      and not coalesce(p.is_deleted, false)
      and p.processus = 'New'
      and p.jour = any (p_jours)
    group by 1, 2, 3, 4;
$$;
comment on function bi.recalculer_niu_profil_jour(date[]) is
    'Recalcule bi.fait_niu_profil_jour pour les jours donnés, depuis etat.profil_anonyme.';

create function bi.recalculer_niu_profil_tout()
returns void
language sql
as $$
    select bi.recalculer_niu_profil_jour(array_agg(jour))
    from (
        select distinct jour from etat.profil_anonyme where jour is not null
        union
        select jour from bi.fait_niu_profil_jour
    ) j;
$$;

-- Contrôles : concordance état ↔ faits ; profils sans sexe ou sans âge.
create function pipeline.controler_profil_niu()
returns table (controle text, statut text, valeur numeric, detail text)
language plpgsql
as $$
declare
    v_etat  bigint;
    v_fait  bigint;
    v_inc   bigint;
begin
    select count(*) into v_etat
    from etat.profil_anonyme p
    where not p._supprime and not coalesce(p.is_deleted, false) and p.processus = 'New' and p.jour is not null;

    select coalesce(sum(f.niu_generes), 0),
           coalesce(sum(f.niu_generes) filter (where f.sexe = 'I' or f.tranche_age = 'inconnu'), 0)
    into v_fait, v_inc
    from bi.fait_niu_profil_jour f;

    insert into pipeline.controle_qualite (controle, statut, valeur, seuil, detail)
    values ('profil_niu_etat_egal_faits', case when v_etat = v_fait then 'ok' else 'echec' end, v_fait - v_etat, 0,
            format('état courant %s, faits %s', v_etat, v_fait)),
           ('profil_niu_sans_sexe_ou_age', case when v_inc = 0 then 'ok' else 'alerte' end, v_inc, 0,
            'NIU dont le genre n''a pas de correspondance validée ou dont l''âge manque');

    return query
        select q.controle, q.statut, q.valeur, q.detail
        from pipeline.controle_qualite q
        order by q.id desc
        limit 2;
end;
$$;

-- Rôles en recette et en production (exemple, comme V2) :
--   pipeline : select/insert/update sur etat.preinscription, etat.profil_anonyme ; select/insert/delete sur
--              bi.fait_preinscription_jour, bi.fait_niu_profil_jour ; execute sur les fonctions de recalcul et
--              bi.region_des_lieux ; insert/update sur bi.source_fraicheur.
--   api      : select sur bi.fait_preinscription_jour et bi.fait_niu_profil_jour (jamais etat ni pipeline).
