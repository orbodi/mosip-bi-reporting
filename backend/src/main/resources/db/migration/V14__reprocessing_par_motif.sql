-- Onglet « En reprocessing » du bloc « Où s'arrêtent les paquets » (décision du responsable, 02/11/2026) : dossiers en
-- reprocessing par étape et motif, même règle que bi.fait_enrolement_jour.en_reprocessing (V13) : en cours dont la
-- dernière transaction MOSIP a le statut REPROCESS. Une partie des en cours de chaque ligne du stock, jamais une
-- ligne de plus : même grain (centre, type, étape, motif, ancienneté), bloqués = ancienneté plus_30j.
-- Valeur 0 par défaut : l'onglet affiche 0 tant que le pipeline n'a pas publié la colonne (mosip-cdc après V14).
-- Les droits de publisher et d'api_reader sur la table ne changent pas.
alter table bi.stock_en_cours_motif add column en_reprocessing int not null default 0;
alter table bi.stock_en_cours_motif add constraint stock_en_cours_motif_reprocessing_inscriptions
    check (en_reprocessing >= 0 and en_reprocessing <= inscriptions);
comment on column bi.stock_en_cours_motif.en_reprocessing is
    'Dont en reprocessing : dernière transaction MOSIP REPROCESS (latest_trn_status_code) ; partie de inscriptions.';
