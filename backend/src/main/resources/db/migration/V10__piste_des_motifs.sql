-- Motifs du bloc « Où s'arrêtent les paquets » : ce qu'il faut vérifier pour chaque motif (décision du 28/10/2026).
-- Le libellé traduit fidèlement le message de MOSIP ; motif_piste dit, en une phrase, ce qu'il veut dire et où chercher
-- (catalogue mosip-cdc/dbt/seeds/ref_regprc_motifs.csv). Migration additive : une colonne facultative par table, aucune
-- donnée existante modifiée ; remplie au passage de publication suivant.

alter table bi.fait_arret_motif_jour add column motif_piste text;
alter table bi.stock_en_cours_motif add column motif_piste text;

comment on column bi.fait_arret_motif_jour.motif_piste is
    'Ce qu''il faut vérifier pour ce motif (catalogue), null pour « Motif non répertorié » sans piste.';
comment on column bi.stock_en_cours_motif.motif_piste is
    'Ce qu''il faut vérifier pour ce motif (catalogue), null pour « Motif non répertorié » sans piste.';
