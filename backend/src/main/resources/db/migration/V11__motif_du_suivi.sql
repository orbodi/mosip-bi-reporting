-- Suivi d'un dossier (I11) : motif de MOSIP du dossier (décision du 29/10/2026).
-- bi.suivi_dossier garde le CODE du motif (status_comment rangé par le catalogue des motifs de mosip-cdc), null pour un
-- dossier sans motif (NIU généré, pas encore reçu). Ses libellés sont dans bi.ref_motif, remplacée à chaque
-- publication : une correction du catalogue s'applique sans republier les 6,4 M de dossiers (publication incrémentale).
-- Le texte de MOSIP d'un dossier n'est jamais écrit dans bi : seulement le message type du catalogue.

alter table bi.suivi_dossier add column motif text;
comment on column bi.suivi_dossier.motif is
    'Code du motif de MOSIP (REFUS_SUPERVISEUR…) des dossiers rejetés, échoués ou en cours ; libellés dans bi.ref_motif.';

create table bi.ref_motif (
    motif        text primary key,
    libelle      text not null,
    commentaire  text,
    piste        text
);
comment on table bi.ref_motif is
    'Catalogue des motifs de MOSIP (mosip-cdc, dbt/seeds/ref_regprc_motifs.csv, sans les règles), remplacé à chaque publication.';
comment on column bi.ref_motif.commentaire is 'Message type de MOSIP pour ce motif (en anglais, tel que MOSIP l''écrit).';
