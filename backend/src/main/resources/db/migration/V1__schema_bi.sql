-- Schéma de la base BI (lecture par l'API, écriture par le pipeline).
-- Migrations en ajout seulement : ne jamais modifier une migration déjà appliquée, en créer une nouvelle.

-- Territoire : Togo > région > préfecture > commune > canton > localité > centre.
create table bi.zone (
    id         bigint generated always as identity primary key,
    niveau     text   not null check (niveau in ('region', 'prefecture', 'commune', 'canton', 'localite', 'centre')),
    code       text   not null unique,
    nom        text   not null,
    parent_id  bigint references bi.zone (id),
    ordre      int    not null default 0,
    check ((niveau = 'region') = (parent_id is null))
);
create index zone_parent_idx on bi.zone (parent_id);
comment on table bi.zone is 'Arborescence du territoire, du niveau région au centre d''enrôlement (CSC).';

-- Fraîcheur des sources : alimente la pastille « Dernière mise à jour » de chaque page.
create table bi.source_fraicheur (
    source             text primary key,
    libelle            text not null,
    ordre              int  not null,
    premiere_donnee    date,
    derniere_donnee    timestamptz,
    dernier_chargement timestamptz
);
comment on column bi.source_fraicheur.premiere_donnee is 'Première date disponible : borne basse du filtre Période.';
comment on column bi.source_fraicheur.derniere_donnee is 'Horodatage de la donnée la plus récente de la source.';
comment on column bi.source_fraicheur.dernier_chargement is 'Fin du dernier chargement réussi par le pipeline.';

-- Enrôlement agrégé au jour et au centre. Contrôle : niu_generes + rejetees + echouees + en_cours = inscriptions.
create table bi.fait_enrolement_jour (
    jour          date   not null,
    centre_id     bigint not null references bi.zone (id),
    sexe          text   not null check (sexe in ('F', 'H', 'I')),
    tranche_age   text   not null check (tranche_age in ('0-5', '6-14', '15-18', '19-25', '>25', 'inconnu')),
    type_demande  text   not null,
    inscriptions  int    not null default 0,
    niu_generes   int    not null default 0,
    en_cours      int    not null default 0,
    echouees      int    not null default 0,
    rejetees      int    not null default 0,
    primary key (jour, centre_id, sexe, tranche_age, type_demande),
    check (niu_generes + rejetees + echouees + en_cours = inscriptions)
);
create index fait_enrolement_jour_centre_idx on bi.fait_enrolement_jour (centre_id, jour);
comment on table bi.fait_enrolement_jour is
    'Inscriptions par jour, centre et profil (docs/indicateurs.md, section Enrôlement). Écrit par le pipeline (dbt).';
