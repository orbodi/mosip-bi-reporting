-- Inscriptions agrégées par jour, centre, sexe, tranche d'âge et type (même grain que bi.fait_enrolement_jour).
-- Le profil (sexe, tranche) vient d'anonymous_profile : jointure à écrire quand le schéma est validé.
select
    i.jour,
    i.code_centre,
    'I'                                            as sexe,         -- à remplacer par le sexe d'anonymous_profile
    'inconnu'                                      as tranche_age,  -- idem
    i.type_demande,
    count(*)                                       as inscriptions,
    count(*) filter (where i.devenir = 'niu')      as niu_generes,
    count(*) filter (where i.devenir = 'en_cours') as en_cours,
    count(*) filter (where i.devenir = 'echouee')  as echouees,
    count(*) filter (where i.devenir = 'rejetee')  as rejetees
from {{ ref('stg_inscriptions') }} as i
group by 1, 2, 3, 4, 5
