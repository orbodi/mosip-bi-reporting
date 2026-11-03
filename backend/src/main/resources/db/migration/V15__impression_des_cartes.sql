-- Impression et remise des cartes (lot 8, décisions du 02/11/2026 ; docs/indicateurs.md, section Impression des cartes ;
-- relevé : mosip-cdc/docs/releve-impression.md). Source : tables printing_* de mosip_regprc, colonnes sans identité.
-- Migration additive : quatre nouvelles tables, alimentées par mosip-cdc/scripts/publier-indicateurs.sh (modèles dbt
-- de dm_impression) ; vides tant que le pipeline ne publie pas. Territoire : centre d'enrôlement lu dans le RID, qui est
-- aussi le lieu de remise. Aucun identifiant de commande, de carte ni de personne.
--
-- Droits (mosip-cdc/sql/traitement/23_droits_bi_impression.sql, exécuté par bi_owner) : publisher écrit ; api_reader
-- lit, comme toutes les tables de bi (privilèges par défaut de 09_droits_bi.sql).

-- I-DEM, I-ATT, I-REJ, I-ANN : commandes par jour de réception (entry_date) et centre, dans leur statut d'aujourd'hui
-- (cohorte). Les annulées sont comptées à part : elles restent aussi dans leur statut.
create table bi.fait_demande_impression_jour (
    jour          date   not null,
    centre_id     bigint not null references bi.zone (id),
    demandes      int    not null check (demandes >= 0),
    envoyees      int    not null check (envoyees >= 0),
    en_attente    int    not null check (en_attente >= 0),
    rejetees      int    not null check (rejetees >= 0),
    non_classees  int    not null check (non_classees >= 0),
    annulees      int    not null check (annulees >= 0),
    primary key (jour, centre_id),
    constraint fait_demande_impression_jour_statuts check (envoyees + en_attente + rejetees + non_classees = demandes),
    constraint fait_demande_impression_jour_annulees check (annulees <= demandes)
);
create index fait_demande_impression_jour_centre_idx on bi.fait_demande_impression_jour (centre_id, jour);
comment on table bi.fait_demande_impression_jour is
    'Commandes d''impression par jour de réception et centre, statut d''aujourd''hui (I-DEM, I-ATT, I-REJ, I-ANN).';
comment on column bi.fait_demande_impression_jour.envoyees is 'prc_status OK : envoyée à l''imprimeur.';
comment on column bi.fait_demande_impression_jour.en_attente is 'prc_status NEW : pas encore envoyée (I-ATT).';
comment on column bi.fait_demande_impression_jour.rejetees is 'prc_status KO (I-REJ).';
comment on column bi.fait_demande_impression_jour.non_classees is 'prc_status sans correspondance (0 attendu).';
comment on column bi.fait_demande_impression_jour.annulees is
    'Dont annulées (événement NEW-PRINT-CANCELED), comptées à part (I-ANN) : partie des demandes, pas un statut.';

-- I-EXP, I-REM, I-AREM : cartes par jour d'expédition et centre, remises ou à remettre aujourd'hui (cohorte).
-- L'ancienneté des cartes à remettre se lit dans le jour d'expédition (calculée par l'API à la lecture).
create table bi.fait_carte_jour (
    jour                date   not null,
    centre_id           bigint not null references bi.zone (id),
    expediees           int    not null check (expediees >= 0),
    remises             int    not null check (remises >= 0),
    remises_hors_ligne  int    not null check (remises_hors_ligne >= 0),
    remises_en_ligne    int    not null check (remises_en_ligne >= 0),
    remises_support     int    not null check (remises_support >= 0),
    remises_autre       int    not null check (remises_autre >= 0),
    a_remettre          int    not null check (a_remettre >= 0),
    primary key (jour, centre_id),
    constraint fait_carte_jour_remises check (remises + a_remettre = expediees),
    constraint fait_carte_jour_modes
        check (remises_hors_ligne + remises_en_ligne + remises_support + remises_autre = remises)
);
create index fait_carte_jour_centre_idx on bi.fait_carte_jour (centre_id, jour);
comment on table bi.fait_carte_jour is
    'Cartes par jour d''expédition et centre, remises ou à remettre aujourd''hui (I-EXP, I-REM, I-AREM).';
comment on column bi.fait_carte_jour.remises_autre is 'Remises dont le mode est absent ou inconnu (0 attendu).';

-- I-DELAI : histogramme du délai du NIU à la carte remise, additif (médiane exacte pour toute zone et toute période).
-- Même cohorte que bi.fait_carte_jour. classe_j : borne basse en jours (0 à 89 jour par jour, puis 90, 120… 690, puis
-- 720 pour deux ans et plus).
create table bi.fait_delai_carte_jour (
    jour       date   not null,
    centre_id  bigint not null references bi.zone (id),
    classe_j   int    not null check (classe_j >= 0),
    cartes     int    not null check (cartes >= 0),
    primary key (jour, centre_id, classe_j)
);
comment on table bi.fait_delai_carte_jour is
    'Histogramme du délai du NIU à la remise de la carte, par jour d''expédition et centre (I-DELAI).';

-- I-ANN par motif : même cohorte que bi.fait_demande_impression_jour ; somme des motifs = annulees.
create table bi.fait_annulation_impression_jour (
    jour           date   not null,
    centre_id      bigint not null references bi.zone (id),
    motif          text   not null,
    motif_libelle  text   not null,
    demandes       int    not null check (demandes >= 0),
    primary key (jour, centre_id, motif)
);
comment on table bi.fait_annulation_impression_jour is
    'Commandes annulées par jour de réception, centre et motif (reason_code de NEW-PRINT-CANCELED, I-ANN).';
comment on column bi.fait_annulation_impression_jour.motif is
    'Code MOSIP du motif (CANCEL_PHOTO…), NON_REPERTORIE s''il est absent du catalogue.';
