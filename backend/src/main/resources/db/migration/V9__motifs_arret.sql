-- Bloc « Où s'arrêtent les paquets » par motif (décision du 26/10/2026) : pour chaque paquet rejeté, échoué ou en cours,
-- l'étape de traitement (reg_stage_name de MOSIP) et le motif tiré du status_comment de MOSIP, rangé par le catalogue
-- mosip-cdc/dbt/seeds/ref_regprc_motifs.csv. Le texte de MOSIP n'est jamais publié : seulement le code du motif, son
-- libellé français et le message type du catalogue (motif_commentaire).
-- Migration additive : deux nouvelles tables, alimentées par mosip-cdc/scripts/publier-indicateurs.sh (modèles dbt
-- fait_arret_motif_jour et stock_en_cours_motif) ; vides tant que le pipeline ne publie pas.
--
-- Droits (mosip-cdc/sql/traitement/16_droits_bi_enrolement.sql, exécuté par bi_owner) : publisher écrit ; api_reader
-- lit, comme toutes les tables de bi (privilèges par défaut de 09_droits_bi.sql).

-- Rejets et échecs par étape et motif, au jour de réception. Contrôle : par devenir, somme = rejetees / echouees de
-- bi.fait_enrolement_jour (test dbt assert_enrolement_motifs_egal_devenir).
create table bi.fait_arret_motif_jour (
    jour               date   not null,
    centre_id          bigint not null references bi.zone (id),
    type_demande       text   not null,
    devenir            text   not null check (devenir in ('rejete', 'echoue')),
    stage              text   not null,
    stage_libelle      text   not null,
    stage_ordre        int    not null,
    motif              text   not null,
    motif_libelle      text   not null,
    motif_commentaire  text,
    inscriptions       int    not null check (inscriptions >= 0),
    primary key (jour, centre_id, type_demande, devenir, stage, motif)
);
create index fait_arret_motif_jour_centre_idx on bi.fait_arret_motif_jour (centre_id, jour);
comment on table bi.fait_arret_motif_jour is
    'Paquets rejetés ou échoués par jour de réception, centre, type, étape (reg_stage_name) et motif (status_comment).';
comment on column bi.fait_arret_motif_jour.motif_commentaire is
    'Message type de MOSIP pour ce motif (catalogue), jamais le texte d''une inscription ; null pour « Motif non répertorié ».';

-- Paquets en cours par étape, motif et ancienneté de la dernière transaction. Stock à l'heure du calcul.
-- « Bloqués » = anciennete plus_30j. Contrôle : total = en_cours de bi.fait_enrolement_jour.
create table bi.stock_en_cours_motif (
    centre_id          bigint      not null references bi.zone (id),
    type_demande       text        not null,
    stage              text        not null,
    stage_libelle      text        not null,
    stage_ordre        int         not null,
    motif              text        not null,
    motif_libelle      text        not null,
    motif_commentaire  text,
    anciennete         text        not null check (anciennete in ('moins_7j', '7_30j', 'plus_30j')),
    inscriptions       int         not null check (inscriptions >= 0),
    calcule_le         timestamptz not null,
    primary key (centre_id, type_demande, stage, motif, anciennete)
);
comment on table bi.stock_en_cours_motif is
    'Paquets en cours par centre, étape (reg_stage_name), motif (status_comment) et ancienneté, à l''heure du calcul.';
