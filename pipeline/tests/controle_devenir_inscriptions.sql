-- Contrôle du dictionnaire : NIU + rejetées + échouées + en cours = inscriptions, pour chaque ligne.
-- Le test échoue s'il renvoie au moins une ligne.
select *
from {{ ref('fait_enrolement_jour') }}
where niu_generes + rejetees + echouees + en_cours <> inscriptions
