-- Volumes de démonstration de la page Enrôlement : profil « demo » seulement (application-demo.yml), à lancer avec
-- le profil dev (mvn spring-boot:run -Dspring-boot.run.profiles=dev,demo). Jamais en recette ni en production.
--
-- Inscriptions FICTIVES du premier au dernier jour de la source « enrolement » (bi.source_fraicheur), réparties sur
-- des centres fictifs, aux ordres de grandeur de la maquette (≈ 3,3 millions). Aucune donnée réelle ni personnelle :
-- des comptes calculés avec un aléa déterministe (le même résultat à chaque exécution).
-- Contrôles respectés : NIU + en cours + échouées + rejetées = inscriptions sur chaque ligne ; total de
-- bi.fait_niu_jour = total des NIU de bi.fait_enrolement_jour ; sexe « I » et tranche « inconnu » partout
-- (docs/decisions.md, pipeline point 1).
--
-- Pré-inscriptions (≈ 607 000 demandes, bi.fait_preinscription_jour) et NIU par sexe et tranche d'âge
-- (bi.fait_niu_profil_jour, répartition de la pyramide de la maquette appliquée aux NIU de bi.fait_niu_jour) : mêmes
-- règles, fictives et déterministes. Total des profils « New » = total des NIU générés de type NEW.
--
-- Incompatible avec la chaîne temps réel (profil temps-reel) : ces faits ne viennent pas de etat.registration et le
-- contrôle « état courant = faits » échouerait. Le script refuse donc de tourner sur une base déjà alimentée par le
-- pipeline. Rejoué à chaque modification de ce fichier : il remplace tous les faits d'enrôlement et de NIU.

do $$
begin
    if exists (select 1 from etat.registration) or exists (select 1 from etat.preinscription)
       or exists (select 1 from etat.profil_anonyme) then
        raise exception 'Volumes de démonstration refusés : le schéma etat est alimenté par le pipeline. '
            'Repartir d''une base vide (docker compose -f deploy/docker-compose.yml down -v) ou retirer le profil demo.';
    end if;
end;
$$;

-- Aléa déterministe dans [0, 1[ tiré d'une clé texte.
create function pg_temp.alea(cle text) returns double precision
language sql immutable
as $$ select (abs(hashtext(cle)::bigint) % 1000003) / 1000003.0 $$;

-- Paramètres par préfecture (maquette) : inscriptions visées, taux de rejet et part restée en cours, en %.
create temporary table demo_prefecture (
    code           text primary key,
    inscriptions   int     not null,
    taux_rejet     numeric not null,
    taux_en_cours  numeric not null
) on commit drop;
insert into demo_prefecture values
    ('SAV-01', 74000, 3.8, 4.9),
    ('SAV-02', 186239, 3.4, 4.4),
    ('SAV-03', 62000, 4.1, 5.2),
    ('SAV-04', 56000, 3.6, 4.7),
    ('SAV-05', 72000, 3.7, 4.8),
    ('KAR-01', 28000, 3.2, 4.7),
    ('KAR-02', 46000, 3.1, 4.5),
    ('KAR-03', 50000, 2.9, 4.3),
    ('KAR-04', 36000, 3.4, 4.9),
    ('KAR-05', 132000, 2.6, 4.0),
    ('KAR-06', 24000, 3.1, 4.6),
    ('KAR-07', 70000, 3.0, 4.4),
    ('CEN-01', 118000, 2.9, 4.2),
    ('CEN-02', 54000, 3.3, 4.7),
    ('CEN-03', 26000, 3.4, 4.8),
    ('CEN-04', 68000, 3.2, 4.6),
    ('CEN-05', 46000, 3.1, 4.5),
    ('PLA-01', 42000, 3.1, 4.6),
    ('PLA-02', 26000, 3.1, 4.5),
    ('PLA-03', 44000, 2.9, 4.3),
    ('PLA-04', 46000, 2.8, 4.2),
    ('PLA-05', 40000, 3.0, 4.5),
    ('PLA-06', 104000, 2.6, 4.0),
    ('PLA-07', 30000, 2.8, 4.2),
    ('PLA-08', 34000, 3.0, 4.4),
    ('PLA-09', 32000, 2.7, 4.1),
    ('PLA-10', 72000, 2.9, 4.3),
    ('PLA-11', 88000, 2.7, 4.1),
    ('PLA-12', 40000, 2.7, 4.1),
    ('MAR-01', 46000, 2.7, 4.4),
    ('MAR-02', 168000, 2.3, 3.8),
    ('MAR-03', 24000, 2.9, 4.6),
    ('MAR-04', 74000, 2.6, 4.1),
    ('MAR-05', 82000, 2.5, 4.0),
    ('MAR-06', 118000, 2.4, 3.9),
    ('GLO-01', 640000, 2.2, 3.8),
    ('GLO-02', 380000, 1.9, 3.5);

-- Centres fictifs : environ un pour 40 000 inscriptions, au moins deux par préfecture.
insert into bi.zone (niveau, code, nom, parent_id, ordre)
select 'centre',
       '2' || lpad((row_number() over (order by r.ordre, p.ordre, n.i))::text, 4, '0'),
       'Centre de démonstration ' || p.nom || ' ' || n.i,
       p.id,
       10 + n.i
from demo_prefecture d
join bi.zone p on p.code = d.code
join bi.zone r on r.id = p.parent_id
cross join lateral generate_series(1, greatest(2, round(d.inscriptions / 40000.0)::int)) as n (i)
on conflict (code) do update
    set nom = excluded.nom,
        parent_id = excluded.parent_id,
        ordre = excluded.ordre;

-- Volume visé par centre : un centre plus actif par préfecture, les autres tirés entre 0,6 et 1,5.
create temporary table demo_centre on commit drop as
select c.id as centre_id, c.code, r.code as region, d.taux_rejet, d.taux_en_cours,
       d.inscriptions * c.poids / sum(c.poids) over (partition by d.code) as volume
from (
    select z.*,
           0.6 + 0.9 * pg_temp.alea('poids ' || z.code)
               + case when row_number() over (partition by z.parent_id order by z.ordre, z.code) = 1 then 0.8 else 0 end
               as poids
    from bi.zone z
    where z.niveau = 'centre'
) c
join bi.zone p on p.id = c.parent_id
join demo_prefecture d on d.code = p.code
join bi.zone r on r.id = p.parent_id;

-- Profil quotidien par région : semaine (samedi réduit, dimanche presque fermé), montée en charge sur six mois,
-- fêtes de fin d'année, et deux campagnes régionales de huit semaines.
create temporary table demo_profil on commit drop as
with bornes as (
    select premiere_donnee as d0, derniere_donnee::date as d1
    from bi.source_fraicheur
    where source = 'enrolement'
),
campagne (region, debut) as (
    values ('SAV', date '2024-03-04'), ('SAV', date '2025-02-03'),
           ('KAR', date '2024-05-06'), ('KAR', date '2025-04-07'),
           ('CEN', date '2024-09-02'), ('CEN', date '2025-06-02'),
           ('PLA', date '2024-11-04'), ('PLA', date '2025-09-01'),
           ('MAR', date '2024-04-01'), ('MAR', date '2025-10-06'),
           ('GLO', date '2024-06-03'), ('GLO', date '2025-11-03')
)
select r.code as region, j.jour,
       (case extract(isodow from j.jour) when 6 then 0.55 when 7 then 0.12 else 1.0 end)
     * least(1.0, 0.55 + 0.45 * (j.jour - b.d0) / 182.0)
     * (case when to_char(j.jour, 'MM-DD') = '01-01' then 0.05
             when to_char(j.jour, 'MM-DD') >= '12-24' or to_char(j.jour, 'MM-DD') <= '01-02' then 0.45
             else 1.0 end)
     * (case when exists (select 1 from campagne k
                          where k.region = r.code and j.jour >= k.debut and j.jour < k.debut + 56) then 1.7
             else 1.0 end) as poids
from bornes b
cross join lateral generate_series(b.d0, b.d1, interval '1 day') as g (t)
cross join lateral (select g.t::date as jour) j
cross join bi.zone r
where r.niveau = 'region' and r.code in ('SAV', 'KAR', 'CEN', 'PLA', 'MAR', 'GLO');

-- Inscriptions par centre et par jour (arrondi aléatoire : le total reste proche du volume visé).
create temporary table demo_jour on commit drop as
select p.jour, c.centre_id, c.code, c.taux_rejet, c.taux_en_cours,
       floor(c.volume * p.poids / s.total * (0.75 + 0.5 * pg_temp.alea('bruit ' || c.code || p.jour))
             + pg_temp.alea('arrondi ' || c.code || p.jour))::int as n
from demo_centre c
join demo_profil p on p.region = c.region
join (select region, sum(poids) as total from demo_profil group by region) s on s.region = c.region;

-- Types de demande : mises à jour ≈ 0,39 %, récupérations de NIU ≈ 0,06 %, le reste en nouvelles inscriptions.
create temporary table demo_type on commit drop as
select j.jour, j.centre_id, j.code, j.taux_rejet, j.taux_en_cours, t.type_demande, t.n
from demo_jour j
cross join lateral (
    select m.maj, least(m.perte, j.n - m.maj) as perte
    from (select floor(j.n * 0.0039 + pg_temp.alea('maj ' || j.code || j.jour))::int as maj,
                 floor(j.n * 0.0006 + pg_temp.alea('perte ' || j.code || j.jour))::int as perte) m
) s
cross join lateral (values ('NEW', j.n - s.maj - s.perte), ('UPDATE', s.maj), ('LOST', s.perte)) as t (type_demande, n)
where t.n > 0;

-- Statuts : rejets et part bloquée selon la préfecture, échecs ≈ 0,28 % ; le reste aboutit à un NIU.
create temporary table demo_statut on commit drop as
select t.jour, t.centre_id, t.code, t.type_demande, t.n, s.rejetees, s.echouees, s.bloquees,
       t.n - s.rejetees - s.echouees - s.bloquees as aboutissent
from demo_type t
cross join lateral (
    select b.rejetees, b.echouees, least(b.bloquees, t.n - b.rejetees - b.echouees) as bloquees
    from (
        select a.rejetees, least(a.echouees, t.n - a.rejetees) as echouees, a.bloquees
        from (select least(t.n, floor(t.n * t.taux_rejet / 100 + pg_temp.alea('rejet ' || t.code || t.jour || t.type_demande))::int) as rejetees,
                     floor(t.n * 0.0028 + pg_temp.alea('echec ' || t.code || t.jour || t.type_demande))::int as echouees,
                     floor(t.n * t.taux_en_cours * 0.7 / 100 + pg_temp.alea('bloque ' || t.code || t.jour || t.type_demande))::int as bloquees) a
    ) b
) s;

-- Délai jusqu'au NIU (médiane ≈ 6 jours) : part cumulée des NIU générés après 2, 4, 6, 9, 15 et 30 jours. Un NIU
-- dont la date tomberait après la dernière donnée n'existe pas encore : l'inscription reste « en cours ».
create temporary table demo_niu on commit drop as
select s.jour, s.centre_id, s.type_demande, s.jour + d.delai as jour_niu,
       (floor(s.aboutissent * d.cumul) - floor(s.aboutissent * d.cumul_avant))::int as niu
from demo_statut s
cross join (values (2, 0.00, 0.10), (4, 0.10, 0.30), (6, 0.30, 0.55),
                   (9, 0.55, 0.75), (15, 0.75, 0.90), (30, 0.90, 1.00)) as d (delai, cumul_avant, cumul);

delete from bi.fait_niu_jour;
delete from bi.fait_enrolement_jour;

-- Reprocessing (V13) : environ 12 % des paquets bloqués, comme le stock observé le 30/10/2026 (7 783 sur ≈ 64 700).
insert into bi.fait_enrolement_jour (jour, centre_id, sexe, tranche_age, type_demande, inscriptions, niu_generes,
                                     en_cours, echouees, rejetees, non_classees, en_reprocessing)
select s.jour, s.centre_id, 'I', 'inconnu', s.type_demande, s.n,
       coalesce(n.generes, 0),
       s.bloquees + coalesce(n.a_venir, 0),
       s.echouees,
       s.rejetees,
       0,
       least(s.bloquees,
             floor(s.bloquees * 0.12 + pg_temp.alea('repro ' || s.code || s.jour || s.type_demande))::int)
from demo_statut s
left join (
    select x.jour, x.centre_id, x.type_demande,
           sum(x.niu) filter (where x.jour_niu <= b.d1) as generes,
           sum(x.niu) filter (where x.jour_niu > b.d1)  as a_venir
    from demo_niu x
    cross join (select derniere_donnee::date as d1 from bi.source_fraicheur where source = 'enrolement') b
    group by x.jour, x.centre_id, x.type_demande
) n on n.jour = s.jour and n.centre_id = s.centre_id and n.type_demande = s.type_demande;

insert into bi.fait_niu_jour (jour, centre_id, type_demande, niu_generes)
select x.jour_niu, x.centre_id, x.type_demande, sum(x.niu)
from demo_niu x
cross join (select derniere_donnee::date as d1 from bi.source_fraicheur where source = 'enrolement') b
where x.jour_niu <= b.d1 and x.niu > 0
group by x.jour_niu, x.centre_id, x.type_demande;

-- ---------------------------------------------------------------------------------------------------------------
-- Pré-inscriptions fictives, du premier au dernier jour de la source « preinscription » (bi.source_fraicheur).
-- Une demande ancienne a presque toujours son rendez-vous ; celles des deux derniers mois l'attendent plus souvent.
-- Les demandes réservées depuis plus d'un mois sont en majorité reprises lors d'une inscription (« honorées »).
-- ---------------------------------------------------------------------------------------------------------------
create temporary table demo_preinscription on commit drop as
with bornes as (
    select premiere_donnee as d0, derniere_donnee::date as d1
    from bi.source_fraicheur
    where source = 'preinscription'
),
jours as (
    select g.t::date as jour, b.d0, b.d1,
           (case extract(isodow from g.t) when 6 then 0.6 when 7 then 0.35 else 1.0 end)
         * least(1.0, 0.5 + 0.5 * (g.t::date - b.d0) / 120.0) as poids
    from bornes b
    cross join lateral generate_series(b.d0, b.d1, interval '1 day') as g (t)
),
volumes as (
    select j.*,
           floor(606850 * j.poids / sum(j.poids) over () * (0.85 + 0.3 * pg_temp.alea('prereg ' || j.jour))
                 + pg_temp.alea('prereg arrondi ' || j.jour))::int as n
    from jours j
)
select v.jour, v.n,
       floor(v.n * (case when v.d1 - v.jour < 60 then 0.32 else 0.07 end)
             + pg_temp.alea('attente ' || v.jour))::int as en_attente,
       case when v.d1 - v.jour < 30 then 0.15 * (v.d1 - v.jour) / 30.0 else 0.82 end as part_honoree
from volumes v;

delete from bi.fait_preinscription_jour;

insert into bi.fait_preinscription_jour (jour, statut, demandes, consommees)
select d.jour, t.statut, t.demandes, t.consommees
from demo_preinscription d
cross join lateral (
    values ('reservee', d.n - least(d.en_attente, d.n),
            floor((d.n - least(d.en_attente, d.n)) * d.part_honoree)::int),
           ('en_attente', least(d.en_attente, d.n), 0)
) as t (statut, demandes, consommees)
where t.demandes > 0;

-- ---------------------------------------------------------------------------------------------------------------
-- NIU générés par sexe et tranche d'âge : chaque (jour de génération, région) de bi.fait_niu_jour (type NEW) est
-- réparti selon la pyramide de la maquette (en % des NIU, femmes puis hommes). Méthode des parts cumulées : la somme
-- des seize cases redonne exactement le total du jour et de la région.
-- ---------------------------------------------------------------------------------------------------------------
create temporary table demo_pyramide (rang int primary key, sexe text, tranche_age text, part numeric)
on commit drop;
insert into demo_pyramide values
    (1, 'F', '60+', 4.1),    (2, 'H', '60+', 2.7),
    (3, 'F', '46-60', 8.4),  (4, 'H', '46-60', 7.2),
    (5, 'F', '36-45', 9.3),  (6, 'H', '36-45', 8.1),
    (7, 'F', '26-35', 12.6), (8, 'H', '26-35', 11.1),
    (9, 'F', '19-25', 9.4),  (10, 'H', '19-25', 8.4),
    (11, 'F', '15-18', 3.8), (12, 'H', '15-18', 3.7),
    (13, 'F', '6-14', 4.3),  (14, 'H', '6-14', 4.6),
    (15, 'F', '0-5', 1.1),   (16, 'H', '0-5', 1.2);

delete from bi.fait_niu_profil_jour;

with niu_region as (
    select f.jour, r.id as region_id, sum(f.niu_generes) as n
    from bi.fait_niu_jour f
    join bi.zone c on c.id = f.centre_id
    join bi.zone p on p.id = c.parent_id
    join bi.zone r on r.id = p.parent_id and r.niveau = 'region'
    where f.type_demande = 'NEW'
    group by f.jour, r.id
),
cumul as (
    select rang, sexe, tranche_age,
           sum(part) over (order by rang) / sum(part) over () as fin,
           (sum(part) over (order by rang) - part) / sum(part) over () as debut
    from demo_pyramide
)
insert into bi.fait_niu_profil_jour (jour, zone_id, sexe, tranche_age, niu_generes)
select n.jour, n.region_id, c.sexe, c.tranche_age, x.niu
from niu_region n
cross join cumul c
cross join lateral (select (floor(n.n * c.fin) - floor(n.n * c.debut))::int as niu) x
where x.niu > 0;
