-- Données de démonstration (profil dev uniquement). Rejouées à chaque modification de ce fichier.
-- Dates de dernière donnée relevées sur le BI actuel (voir docs/sources-mosip.md).

insert into bi.source_fraicheur (source, libelle, ordre, premiere_donnee, derniere_donnee, dernier_chargement) values
    ('enrolement',        'Enrôlement',            1, '2024-01-01', '2026-01-14 11:42:00+00', null),
    ('cartes',            'Impression des cartes', 2, '2024-02-01', '2026-01-14 11:59:00+00', null),
    ('abis',              'ABIS',                  3, '2024-01-01', '2026-07-13 11:59:00+00', null),
    ('idps',              'IDPS',                  4, '2026-07-03', '2026-07-03 17:09:00+00', null),
    ('authentifications', 'Authentifications',     5, '2025-02-01', '2026-01-14 11:05:00+00', null),
    ('preinscription',    'Pré-inscription',       6, '2024-01-01', '2026-01-14 11:28:00+00', null)
on conflict (source) do update
    set libelle = excluded.libelle,
        ordre = excluded.ordre,
        premiere_donnee = excluded.premiere_donnee,
        derniere_donnee = excluded.derniere_donnee;

-- Les six régions, du nord au sud (codes provisoires en attendant le référentiel MOSIP).
insert into bi.zone (niveau, code, nom, parent_id, ordre) values
    ('region', 'SAV', 'Savanes',    null, 1),
    ('region', 'KAR', 'Kara',       null, 2),
    ('region', 'CEN', 'Centrale',   null, 3),
    ('region', 'PLA', 'Plateaux',   null, 4),
    ('region', 'MAR', 'Maritime',   null, 5),
    ('region', 'GLO', 'Grand Lomé', null, 6)
on conflict (code) do update
    set nom = excluded.nom,
        ordre = excluded.ordre;

-- Préfectures des contours de la maquette (geoBoundaries : 37 des 39 préfectures officielles), du nord au sud dans
-- chaque région. Codes provisoires en attendant master.location ; les noms servent à relier les contours de la carte.
insert into bi.zone (niveau, code, nom, parent_id, ordre)
select 'prefecture', p.code, p.nom, r.id, p.ordre
from (values
    ('SAV-01', 'Cinkassé', 'SAV', 1),
    ('SAV-02', 'Tône', 'SAV', 2),
    ('SAV-03', 'Kpendjal', 'SAV', 3),
    ('SAV-04', 'Tandjouaré', 'SAV', 4),
    ('SAV-05', 'Oti', 'SAV', 5),
    ('KAR-01', 'Kéran', 'KAR', 1),
    ('KAR-02', 'Doufelgou', 'KAR', 2),
    ('KAR-03', 'Binah', 'KAR', 3),
    ('KAR-04', 'Dankpen', 'KAR', 4),
    ('KAR-05', 'Kozah', 'KAR', 5),
    ('KAR-06', 'Assoli', 'KAR', 6),
    ('KAR-07', 'Bassar', 'KAR', 7),
    ('CEN-01', 'Tchaoudjo', 'CEN', 1),
    ('CEN-02', 'Tchamba', 'CEN', 2),
    ('CEN-03', 'Mô', 'CEN', 3),
    ('CEN-04', 'Sotouboua', 'CEN', 4),
    ('CEN-05', 'Blitta', 'CEN', 5),
    ('PLA-01', 'Est-Mono', 'PLA', 1),
    ('PLA-02', 'Akébou', 'PLA', 2),
    ('PLA-03', 'Anié', 'PLA', 3),
    ('PLA-04', 'Amou', 'PLA', 4),
    ('PLA-05', 'Wawa', 'PLA', 5),
    ('PLA-06', 'Ogou', 'PLA', 6),
    ('PLA-07', 'Danyi', 'PLA', 7),
    ('PLA-08', 'Moyen-Mono', 'PLA', 8),
    ('PLA-09', 'Kpélé', 'PLA', 9),
    ('PLA-10', 'Haho', 'PLA', 10),
    ('PLA-11', 'Kloto', 'PLA', 11),
    ('PLA-12', 'Agou', 'PLA', 12),
    ('MAR-01', 'Yoto', 'MAR', 1),
    ('MAR-02', 'Zio', 'MAR', 2),
    ('MAR-03', 'Bas-Mono', 'MAR', 3),
    ('MAR-04', 'Avé', 'MAR', 4),
    ('MAR-05', 'Vo', 'MAR', 5),
    ('MAR-06', 'Lacs', 'MAR', 6),
    ('GLO-01', 'Golfe', 'GLO', 1),
    ('GLO-02', 'Lomé', 'GLO', 2)
) as p (code, nom, region, ordre)
join bi.zone r on r.code = p.region
on conflict (code) do update
    set nom = excluded.nom,
        parent_id = excluded.parent_id,
        ordre = excluded.ordre;

-- Centres fictifs (deux par région) utilisés par le simulateur MOSIP du pipeline temps réel
-- (pipeline/simulateur) : le code est le préfixe à 5 chiffres des RID simulés. Rattachés à une préfecture de leur
-- région en attendant le référentiel master.location / master.registration_center.
insert into bi.zone (niveau, code, nom, parent_id, ordre)
select 'centre', c.code, c.nom, p.id, c.ordre
from (values
    ('10011', 'Centre de démonstration Savanes 1',    'SAV-02', 1),
    ('10012', 'Centre de démonstration Savanes 2',    'SAV-01', 2),
    ('10021', 'Centre de démonstration Kara 1',       'KAR-05', 1),
    ('10022', 'Centre de démonstration Kara 2',       'KAR-07', 2),
    ('10031', 'Centre de démonstration Centrale 1',   'CEN-01', 1),
    ('10032', 'Centre de démonstration Centrale 2',   'CEN-04', 2),
    ('10041', 'Centre de démonstration Plateaux 1',   'PLA-06', 1),
    ('10042', 'Centre de démonstration Plateaux 2',   'PLA-11', 2),
    ('10051', 'Centre de démonstration Maritime 1',   'MAR-02', 1),
    ('10052', 'Centre de démonstration Maritime 2',   'MAR-06', 2),
    ('10061', 'Centre de démonstration Grand Lomé 1', 'GLO-01', 1),
    ('10062', 'Centre de démonstration Grand Lomé 2', 'GLO-02', 2)
) as c (code, nom, prefecture, ordre)
join bi.zone p on p.code = c.prefecture
on conflict (code) do update
    set nom = excluded.nom,
        parent_id = excluded.parent_id,
        ordre = excluded.ordre;

-- Regroupement des statuts : DÉMONSTRATION SEULEMENT (accord du 16/10/2026 pour le développement). Codes de
-- l'énumération RegistrationStatusCode de MOSIP v1.1.5 ; la correspondance réelle reste à valider par l'équipe MOSIP
-- et n'est jamais chargée en recette ni en production par ce fichier.
insert into pipeline.correspondance_statut (status_code, statut_regroupe, valide_par, valide_le, commentaire) values
    ('PROCESSED',        'abouti',   null, null, 'démonstration, à valider par l''équipe MOSIP'),
    ('PROCESSING',       'en_cours', null, null, 'démonstration, à valider par l''équipe MOSIP'),
    ('REJECTED',         'rejete',   null, null, 'démonstration, à valider par l''équipe MOSIP'),
    ('FAILED',           'echoue',   null, null, 'démonstration, à valider par l''équipe MOSIP'),
    ('REPROCESS_FAILED', 'echoue',   null, null, 'démonstration, à valider par l''équipe MOSIP')
on conflict (status_code) do update
    set statut_regroupe = excluded.statut_regroupe,
        commentaire = excluded.commentaire;

-- Regroupement des statuts de pré-inscription : DÉMONSTRATION SEULEMENT. Codes relevés sur mosip_prereg le
-- 14/10/2026 (Booked, Pending_Appointment ; Expired attendu par MOSIP, absent de l'instance). La correspondance réelle
-- reste à valider par l'équipe MOSIP et n'est jamais chargée en recette ni en production par ce fichier.
insert into pipeline.correspondance_statut_preinscription (status_code, statut_regroupe, valide_par, valide_le,
                                                           commentaire) values
    ('Pending_Appointment', 'en_attente', null, null, 'démonstration, à valider par l''équipe MOSIP'),
    ('Booked',              'reservee',   null, null, 'démonstration, à valider par l''équipe MOSIP'),
    ('Expired',             'expiree',    null, null, 'démonstration, à valider par l''équipe MOSIP')
on conflict (status_code) do update
    set statut_regroupe = excluded.statut_regroupe,
        commentaire = excluded.commentaire;

-- Genre du profil anonymisé → sexe : DÉMONSTRATION SEULEMENT (valeurs du simulateur et des volumes de démonstration).
-- Les valeurs réelles de « gender » se relèvent sur idrepo.anonymous_profile et se font valider par l'équipe MOSIP.
insert into pipeline.correspondance_sexe (genre, sexe, valide_par, valide_le, commentaire) values
    ('Female', 'F', null, null, 'démonstration, à valider par l''équipe MOSIP'),
    ('Male',   'H', null, null, 'démonstration, à valider par l''équipe MOSIP')
on conflict (genre) do update
    set sexe = excluded.sexe,
        commentaire = excluded.commentaire;
