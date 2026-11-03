-- Lot 8d (03/11/2026 ; docs/indicateurs.md, I-ERR et I-SANS) : erreurs d'envoi à l'IDPS et NIU sans commande
-- d'impression. Migration additive, alimentée par mosip-cdc/scripts/publier-indicateurs.sh.
-- Droits : mosip-cdc/sql/traitement/24_droits_bi_impression_8d.sql (bi_owner).

-- I-ERR : commandes qui ont eu au moins une erreur d'envoi à l'IDPS (PRINT-REQUEST-ERR), parmi les demandes du jour
-- de réception. Valeur 0 par défaut : 0 à l'écran tant que le pipeline ne publie pas la colonne.
alter table bi.fait_demande_impression_jour add column erreurs_idps int not null default 0;
alter table bi.fait_demande_impression_jour add constraint fait_demande_impression_jour_erreurs_idps
    check (erreurs_idps >= 0 and erreurs_idps <= demandes);
comment on column bi.fait_demande_impression_jour.erreurs_idps is
    'Dont commandes avec au moins une erreur d''envoi à l''IDPS (I-ERR), même renvoyées ensuite : partie des demandes.';

-- I-SANS : NIU de première inscription (NEW) sans aucune commande d'impression, par centre et ancienneté du NIU
-- (moins_7j : commande normalement en route ; plus_7j : bloqué). Stock à l'heure du calcul.
create table bi.stock_niu_sans_commande (
    centre_id       bigint      not null references bi.zone (id),
    anciennete      text        not null check (anciennete in ('moins_7j', 'plus_7j')),
    niu             int         not null check (niu >= 0),
    plus_ancien_le  timestamptz not null,
    calcule_le      timestamptz not null,
    primary key (centre_id, anciennete)
);
comment on table bi.stock_niu_sans_commande is
    'NIU de première inscription sans commande d''impression, par centre et ancienneté du NIU (I-SANS), à l''heure du calcul.';
