-- Une ligne par inscription, avec son statut regroupé. Règle de regroupement à valider avec l'équipe MOSIP
-- (docs/indicateurs.md, statuts ; ne pas mélanger status_code et latest_trn_status_code).
select
    r.id                                  as rid,
    substr(r.id, 1, 5)                    as code_centre,
    cast(r.cr_dtimes as date)             as jour,
    r.reg_type                            as type_demande,
    case
        when r.status_code = 'PROCESSED' then 'niu'
        when r.status_code = 'REJECTED' then 'rejetee'
        when r.status_code in ('FAILED', 'REPROCESS_FAILED') then 'echouee'
        else 'en_cours'
    end                                   as devenir
from {{ source('brut', 'registration') }} as r
