-- Lot E2 (07/11/2026) : profil des inscriptions dans bi.fait_enrolement_jour, pour les filtres Sexe, Tranche d'âge et
-- Nationalité de l'Exploration. Le pipeline (dm_enrolement.fait_enrolement_jour) relie chaque inscription à la réponse
-- de l'ID Repository (lot 6) ; seules les inscriptions devenues NIU et déjà enrichies ont un profil, les autres restent
-- en sexe « I », tranche « inconnu », nationalité « Non renseignée ».
--
-- Migration compatible avec la publication d'avant le lot : la nationalité a une valeur par défaut, et les anciennes
-- lignes (toutes en « I », « inconnu ») restent valides. À appliquer AVANT le git pull de mosip-cdc qui écrit la
-- colonne (sinon la publication s'arrête).

alter table bi.fait_enrolement_jour add column nationalite text not null default 'Non renseignée';

-- Tranches d'âge de la pyramide (comme bi.fait_niu_profil_jour, V4) au lieu des cinq tranches de V1.
alter table bi.fait_enrolement_jour drop constraint fait_enrolement_jour_tranche_age_check;
alter table bi.fait_enrolement_jour add constraint fait_enrolement_jour_tranche_age_check
    check (tranche_age in ('0-5', '6-14', '15-18', '19-25', '26-35', '36-45', '46-60', '60+', 'inconnu'));

alter table bi.fait_enrolement_jour drop constraint fait_enrolement_jour_pkey;
alter table bi.fait_enrolement_jour add constraint fait_enrolement_jour_pkey
    primary key (jour, centre_id, sexe, tranche_age, type_demande, nationalite);

comment on column bi.fait_enrolement_jour.sexe is
    'Sexe de l''ID Repository (F, H) pour les inscriptions devenues NIU et enrichies ; I sinon (non renseigné).';
comment on column bi.fait_enrolement_jour.tranche_age is
    'Âge à la réception du paquet (années révolues, année et mois de naissance de l''ID Repository), tranches de la '
    'pyramide ; inconnu sans profil.';
comment on column bi.fait_enrolement_jour.nationalite is
    'Libellé de la liste MOSIP « nationality » (ou la valeur de l''ID Repository telle quelle) ; « Non renseignée » '
    'sans profil.';
