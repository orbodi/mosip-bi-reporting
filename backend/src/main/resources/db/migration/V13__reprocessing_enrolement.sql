-- Dossiers en reprocessing (décision du responsable, 31/10/2026) : bloc « Devenir des inscriptions », encart de la
-- carte En cours. Un dossier est en reprocessing quand il est en cours (devenir en_cours) et que sa dernière
-- transaction MOSIP a le statut REPROCESS (regprc.registration.latest_trn_status_code) : MOSIP le reprendra. C'est
-- une partie des en cours, jamais un statut de plus : la somme des statuts reste égale aux inscriptions.
-- Les demandes de mise à jour (UPDATE, RES_UPDATE) et de NIU perdu (LOST) n'ont pas besoin de colonne : elles se
-- lisent dans type_demande.
-- Valeur 0 par défaut : l'encart affiche 0 tant que le pipeline n'a pas publié la colonne (mosip-cdc après V13).
alter table bi.fait_enrolement_jour add column en_reprocessing int not null default 0;
alter table bi.fait_enrolement_jour add constraint fait_enrolement_jour_reprocessing_en_cours
    check (en_reprocessing >= 0 and en_reprocessing <= en_cours);
comment on column bi.fait_enrolement_jour.en_reprocessing is
    'Dont en cours dont la dernière transaction MOSIP est REPROCESS (latest_trn_status_code) : partie de en_cours.';
