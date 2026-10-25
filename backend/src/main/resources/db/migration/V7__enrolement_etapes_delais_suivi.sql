-- Page Enrôlement v3 : étapes d'arrêt, paquets en cours, délais, synchronisés non reçus, suivi d'un dossier.
-- Conception : mosip-cdc/docs/conception-enrolement.md § 4 ; indicateurs I5 à I11 de mosip-cdc/docs/releve-enrolement.md.
-- Migration additive : de nouvelles tables, aucune donnée existante modifiée. Alimentées par
-- mosip-cdc/scripts/publier-indicateurs.sh (modèles dbt de dm_enrolement) ; vides tant que le pipeline ne publie pas.
--
-- Droits (mosip-cdc/sql/traitement/16_droits_bi_enrolement.sql, exécuté par bi_owner) : publisher écrit ; api_reader
-- lit, comme toutes les tables de bi (privilèges par défaut de 09_droits_bi.sql).

-- I5, I6 : rejets et échecs par étape, au jour de réception (lecture cohorte, comme bi.fait_enrolement_jour).
-- etape : code de transaction MOSIP (VALIDATE_PACKET…), ou REFUS_POSTE pour un rejet décidé au poste d'enrôlement.
-- Contrôle : par devenir, somme = rejetees / echouees de bi.fait_enrolement_jour.
create table bi.fait_arret_etape_jour (
    jour           date   not null,
    centre_id      bigint not null references bi.zone (id),
    type_demande   text   not null,
    devenir        text   not null check (devenir in ('rejete', 'echoue')),
    etape          text   not null,
    etape_libelle  text   not null,
    etape_ordre    int    not null,
    inscriptions   int    not null check (inscriptions >= 0),
    primary key (jour, centre_id, type_demande, devenir, etape)
);
create index fait_arret_etape_jour_centre_idx on bi.fait_arret_etape_jour (centre_id, jour);
comment on table bi.fait_arret_etape_jour is
    'Paquets rejetés ou échoués par jour de réception, centre, type et étape d''arrêt (I5, I6).';

-- I7 : paquets en cours, par étape et ancienneté de la dernière transaction. Stock à l'heure du calcul.
-- « Bloqués » = anciennete plus_30j. Contrôle : total = en_cours de bi.fait_enrolement_jour.
create table bi.stock_en_cours (
    centre_id      bigint      not null references bi.zone (id),
    type_demande   text        not null,
    etape          text        not null,
    etape_libelle  text        not null,
    etape_ordre    int         not null,
    anciennete     text        not null check (anciennete in ('moins_7j', '7_30j', 'plus_30j')),
    inscriptions   int         not null check (inscriptions >= 0),
    calcule_le     timestamptz not null,
    primary key (centre_id, type_demande, etape, anciennete)
);
comment on table bi.stock_en_cours is
    'Paquets en cours par centre, étape et ancienneté de la dernière transaction (I7), à l''heure du calcul.';

-- I8, I9 : histogrammes de délais, additifs (médiane et 90e centile exacts pour toute zone et toute période).
-- mesure reception_niu : de la réception au NIU, au jour du NIU ; enrolement_reception : de l'enrôlement au poste à la
-- réception, au jour de réception. classe_h : borne basse en heures (0 à 47 heure par heure, puis 48, 72, 96…).
create table bi.fait_delai_jour (
    jour           date   not null,
    centre_id      bigint not null references bi.zone (id),
    type_demande   text   not null,
    mesure         text   not null check (mesure in ('reception_niu', 'enrolement_reception')),
    classe_h       int    not null check (classe_h >= 0),
    paquets        int    not null check (paquets >= 0),
    primary key (jour, centre_id, type_demande, mesure, classe_h)
);
create index fait_delai_jour_mesure_idx on bi.fait_delai_jour (mesure, jour);
comment on table bi.fait_delai_jour is 'Histogrammes des délais réception → NIU et enrôlement → réception (I8, I9).';

-- I10 : paquets synchronisés par le poste mais pas encore reçus par MOSIP. Stock à l'heure du calcul.
create table bi.stock_synchro_non_recue (
    centre_id         bigint      not null references bi.zone (id),
    anciennete        text        not null check (anciennete in ('moins_7j', 'plus_7j')),
    paquets           int         not null check (paquets >= 0),
    plus_ancienne_le  timestamptz not null,
    calcule_le        timestamptz not null,
    primary key (centre_id, anciennete)
);
comment on table bi.stock_synchro_non_recue is
    'Paquets synchronisés non reçus par centre et ancienneté (I10) : moins de 7 jours = en transit probable.';

-- Profil des NIU par nationalité (lot 6, enrichissement démographique) : vide d'ici là.
create table bi.fait_niu_nationalite_jour (
    jour          date   not null,
    zone_id       bigint not null references bi.zone (id),
    nationalite   text   not null,
    niu_generes   int    not null check (niu_generes >= 0),
    primary key (jour, zone_id, nationalite)
);
comment on table bi.fait_niu_nationalite_jour is 'NIU générés par jour, région et nationalité (enrichissement, lot 6).';

-- I11 : suivi d'un dossier. Une ligne par RID reçu ou synchronisé, indexée par l'EMPREINTE du RID :
-- hmac(rid, clé, 'sha256'), clé SUIVI_HMAC_CLE connue de la publication et de l'API seulement. Le RID n'est jamais
-- écrit ici : sans la clé, une copie de la table ne permet pas de retrouver les RID.
-- Mise à jour par lots (seules les lignes changées depuis la publication précédente, repérées par maj_le).
create table bi.suivi_dossier (
    empreinte                bytea       primary key,
    centre_id                bigint      not null references bi.zone (id),
    type_demande             text        not null,
    enrole_le                timestamptz,
    synchronise_le           timestamptz,
    refus_poste              boolean     not null,
    recu_le                  timestamptz,
    niu_le                   timestamptz,
    devenir                  text        not null
        check (devenir in ('niu', 'en_cours', 'echoue', 'rejete', 'non_classe', 'non_recu')),
    etape                    text,
    etape_libelle            text,
    etape_statut             text,
    derniere_transaction_le  timestamptz,
    maj_le                   timestamptz not null
);
create index suivi_dossier_maj_le_idx on bi.suivi_dossier (maj_le);
comment on table bi.suivi_dossier is
    'Suivi d''un dossier (I11) : jalons, étape et devenir par empreinte HMAC du RID, jamais le RID.';
comment on column bi.suivi_dossier.maj_le is
    'Heure du passage dbt qui a écrit la ligne ; la publication reprend les lignes plus récentes que le maximum publié.';
