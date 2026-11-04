-- Authentifications (lot 9, décisions des 03 et 04/11/2026 ; docs/indicateurs.md, section Authentifications ; relevé :
-- mosip-cdc/docs/releve-authentification.md). Source : ida.auth_transaction et ida.otp_transaction de mosip_ida, colonnes
-- sans identité. Migration additive : quatre nouvelles tables, alimentées par mosip-cdc/scripts/publier-indicateurs.sh
-- (modèles dbt de dm_authentification) ; vides tant que le pipeline ne publie pas. Pas de territoire : une
-- authentification n'a pas de lieu. Aucun identifiant de personne ni de transaction, aucun texte libre.
--
-- Deux périmètres jamais additionnés (option A, 03/11/2026) : usagers (partenaires, portail du résident, USSD) et
-- paquets (vérifications biométriques faites par MOSIP pendant le traitement des paquets).
--
-- Droits (mosip-cdc/sql/traitement/26_droits_bi_authentification.sql, exécuté par bi_owner) : publisher écrit ;
-- api_reader lit, comme toutes les tables de bi (privilèges par défaut de 09_droits_bi.sql).

-- A-REQ, A-OK, A-KO, A-TYPE, A-CAUSE, A-PART : authentifications par jour d'enregistrement, appelant, type, statut et
-- motif, hors demandes de code OTP (bi.fait_demande_otp_jour).
create table bi.fait_authentification_jour (
    jour               date not null,
    perimetre          text not null check (perimetre in ('usagers', 'paquets', 'non_classe')),
    canal              text not null check (canal in ('partenaire', 'portail', 'ussd', 'paquets', 'non_classe')),
    appelant_id        text not null,
    appelant           text not null,
    type               text not null
        check (type in ('biometrique', 'otp', 'demographique', 'combinee', 'sans_mode', 'non_classe')),
    statut             text not null check (statut in ('reussie', 'echouee', 'non_classe')),
    motif              text not null,
    authentifications  int  not null check (authentifications > 0),
    primary key (jour, appelant_id, type, statut, motif),
    constraint fait_authentification_jour_motif check ((statut = 'echouee') = (motif <> 'AUCUN'))
);
create index fait_authentification_jour_perimetre_idx on bi.fait_authentification_jour (perimetre, jour);
comment on table bi.fait_authentification_jour is
    'Authentifications par jour (cr_dtimes), appelant, type, statut et motif ; hors demandes de code OTP.';
comment on column bi.fait_authentification_jour.perimetre is
    'usagers (partenaires, portail du résident, USSD) ou paquets (traitement des paquets) : jamais additionnés.';
comment on column bi.fait_authentification_jour.appelant_id is
    'Code MOSIP de l''appelant (requested_entity_id : partenaire ou client MOSIP, une organisation) : clé, non affichée.';
comment on column bi.fait_authentification_jour.appelant is 'Nom affiché : Atos, Portail du résident, USSD…';
comment on column bi.fait_authentification_jour.type is
    'Famille des modalités : biometrique (empreinte, iris, visage), otp, demographique, combinee (plusieurs familles), '
    'sans_mode (eKYC sans modalité), non_classe (code inconnu).';
comment on column bi.fait_authentification_jour.motif is
    'AUCUN pour une réussie ou non classée ; sinon code de bi.ref_motif_authentification (AUTRE : non répertorié).';

-- Demandes d'envoi d'un code OTP (OTP-REQUEST) : pas des authentifications, comptées à part.
create table bi.fait_demande_otp_jour (
    jour         date not null,
    perimetre    text not null check (perimetre in ('usagers', 'paquets', 'non_classe')),
    canal        text not null check (canal in ('partenaire', 'portail', 'ussd', 'paquets', 'non_classe')),
    appelant_id  text not null,
    appelant     text not null,
    demandes     int  not null check (demandes >= 0),
    refusees     int  not null check (refusees >= 0),
    primary key (jour, appelant_id),
    constraint fait_demande_otp_jour_refusees check (refusees <= demandes)
);
comment on table bi.fait_demande_otp_jour is
    'Demandes d''envoi d''un code OTP par jour et appelant (OTP-REQUEST, pas une authentification) ; refusées : statut N.';

-- A-OTP : codes OTP par jour de demande, dont utilisés (ida.otp_transaction ne dit pas quel appelant l'a demandé).
create table bi.fait_code_otp_jour (
    jour      date primary key,
    codes     int  not null check (codes >= 0),
    utilises  int  not null check (utilises >= 0),
    constraint fait_code_otp_jour_utilises check (utilises <= codes)
);
comment on table bi.fait_code_otp_jour is
    'Codes OTP par jour de demande (ida.otp_transaction), dont utilisés ; les autres n''ont jamais servi (expirés).';

-- Libellés des motifs d'échec (seeds/ref_ida_motifs.csv de mosip-cdc, plus AUTRE), remplacés à chaque passage.
create table bi.ref_motif_authentification (
    motif    text primary key,
    libelle  text not null,
    ordre    int  not null
);
comment on table bi.ref_motif_authentification is 'Libellé français de chaque motif d''échec d''authentification.';
