-- Profil et territoire des pré-inscriptions. Source : champs extraits de l'API de pré-inscription MOSIP par le pipeline
-- mosip-cdc (genre, année et mois de naissance, nationalité, préfecture de résidence), jamais d'autre donnée d'identité.

-- Répartition par sexe, tranche d'âge (à la date de la demande) et nationalité. Contrôle : la somme des demandes égale
-- celle de bi.fait_preinscription_jour sur la même période.
create table bi.fait_preinscription_profil_jour (
    jour         date not null,
    sexe         text not null check (sexe in ('F', 'H', 'I')),
    tranche_age  text not null check (tranche_age in ('0-5', '6-14', '15-18', '19-25', '26-35', '36-45', '46-60', '60+',
                                                      'inconnu')),
    nationalite  text not null,
    demandes     int  not null check (demandes >= 0),
    primary key (jour, sexe, tranche_age, nationalite)
);
comment on table bi.fait_preinscription_profil_jour is
    'Pré-inscriptions par jour de création, sexe, tranche d''âge et nationalité (libellé MOSIP).';
comment on column bi.fait_preinscription_profil_jour.nationalite is
    'Libellé de la liste MOSIP « nationality » ; « Non renseignée » si la demande n''est pas enrichie ou sans nationalité.';

-- Pré-inscriptions par préfecture de résidence déclarée. Les demandes sans préfecture connue n'y figurent pas.
create table bi.fait_preinscription_zone_jour (
    jour      date   not null,
    zone_id   bigint not null references bi.zone (id),
    demandes  int    not null check (demandes >= 0),
    primary key (jour, zone_id)
);
create index fait_preinscription_zone_jour_zone_idx on bi.fait_preinscription_zone_jour (zone_id, jour);
comment on table bi.fait_preinscription_zone_jour is
    'Pré-inscriptions par jour de création et préfecture de résidence déclarée (bi.zone, niveau préfecture).';
