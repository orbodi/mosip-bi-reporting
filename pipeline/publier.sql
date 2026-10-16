-- Publication des calculs dbt (schéma bi_calc) vers les tables lues par l'API (schéma bi), en une transaction.
-- Lancé après « dbt build » réussi : psql -v ON_ERROR_STOP=1 -f publier.sql
begin;

delete from bi.fait_enrolement_jour;
insert into bi.fait_enrolement_jour
    (jour, centre_id, sexe, tranche_age, type_demande, inscriptions, niu_generes, en_cours, echouees, rejetees)
select f.jour, z.id, f.sexe, f.tranche_age, f.type_demande,
       f.inscriptions, f.niu_generes, f.en_cours, f.echouees, f.rejetees
from bi_calc.fait_enrolement_jour as f
join bi.zone as z on z.niveau = 'centre' and z.code = f.code_centre;

update bi.source_fraicheur
set derniere_donnee = (select max(cr_dtimes) from brut.registration)::timestamptz,  -- horodatage exact, pas seulement le jour
    dernier_chargement = now()
where source = 'enrolement';

commit;
