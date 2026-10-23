-- Sexe des pré-inscriptions. Source : genre renvoyé par l'API de pré-inscription MOSIP (enrichissement du pipeline
-- mosip-cdc, sans aucune autre donnée d'identité) ; F ou H selon le genre MOSIP (FLE, MLE), I (inconnu) tant que la
-- demande n'est pas enrichie ou que l'API ne donne pas de genre.
-- Valeur par défaut « I » : un chargement qui ne renseigne pas le sexe reste valide.

alter table bi.fait_preinscription_jour
    add column sexe text not null default 'I' check (sexe in ('F', 'H', 'I'));
alter table bi.fait_preinscription_jour drop constraint fait_preinscription_jour_pkey;
alter table bi.fait_preinscription_jour add primary key (jour, statut, sexe);

comment on table bi.fait_preinscription_jour is
    'Pré-inscriptions par jour de création (cr_dtimes), statut regroupé et sexe.';
comment on column bi.fait_preinscription_jour.sexe is
    'F ou H selon le genre de l''API de pré-inscription MOSIP ; I = inconnu (demande pas encore enrichie, ou sans genre).';
