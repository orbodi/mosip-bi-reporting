-- Page Enrôlement, bloc « Inscriptions et NIU par semaine » (docs/plans/enrolement.md, décision P2 : lecture flux).
-- Migration additive : une nouvelle table de faits, aucune donnée existante modifiée.
--
-- Les NIU y sont rattachés au jour où ils ont été générés, et non au jour de réception de l'inscription
-- (bi.fait_enrolement_jour, lecture cohorte). Sur toute la durée, les deux totaux doivent concorder :
-- somme de fait_niu_jour.niu_generes = somme de fait_enrolement_jour.niu_generes (contrôle des tests).
--
-- Alimentation réelle : lot A du pipeline (date = transaction « NIU généré », docs/datamart.md § 5.2), règle à
-- valider avec l'équipe MOSIP. D'ici là, seules les données de démonstration (profil demo, db/demo) la remplissent ;
-- ailleurs elle reste vide et l'API le signale (niuDisponibles = false), sans jamais estimer.

create table bi.fait_niu_jour (
    jour          date   not null,
    centre_id     bigint not null references bi.zone (id),
    type_demande  text   not null,
    niu_generes   int    not null check (niu_generes >= 0),
    primary key (jour, centre_id, type_demande)
);
create index fait_niu_jour_centre_idx on bi.fait_niu_jour (centre_id, jour);
comment on table bi.fait_niu_jour is
    'NIU générés par jour de génération, centre et type de demande (lecture flux). Alimenté par le lot A du pipeline.';
comment on column bi.fait_niu_jour.jour is 'Jour de génération du NIU (heure du Togo, UTC+0).';

-- Rôles en recette et en production (exemple, comme V2) :
--   pipeline : select/insert/delete sur bi.fait_niu_jour ;
--   api      : select sur bi.fait_niu_jour.
