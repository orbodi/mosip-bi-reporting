-- Données de démonstration (profil dev uniquement). Rejouées à chaque modification de ce fichier.
-- Dates de dernière donnée relevées sur le BI actuel (voir docs/sources-mosip.md).

insert into bi.source_fraicheur (source, libelle, ordre, premiere_donnee, derniere_donnee, dernier_chargement) values
    ('enrolement',        'Enrôlement',            1, '2024-01-01', '2026-01-14 11:42:00+00', null),
    ('cartes',            'Impression des cartes', 2, '2024-02-01', '2026-01-14 11:59:00+00', null),
    ('abis',              'ABIS',                  3, '2024-01-01', '2026-07-13 11:59:00+00', null),
    ('idps',              'IDPS',                  4, '2026-07-03', '2026-07-03 17:09:00+00', null),
    ('authentifications', 'Authentifications',     5, '2025-02-01', '2026-01-14 11:05:00+00', null)
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

-- Centres fictifs (deux par région) utilisés par le simulateur MOSIP du pipeline temps réel
-- (pipeline/simulateur) : le code est le préfixe à 5 chiffres des RID simulés. Rattachés directement à la région
-- en attendant le référentiel master.location / master.registration_center.
insert into bi.zone (niveau, code, nom, parent_id, ordre)
select 'centre', c.code, c.nom, r.id, c.ordre
from (values
    ('10011', 'Centre de démonstration Savanes 1',    'SAV', 1),
    ('10012', 'Centre de démonstration Savanes 2',    'SAV', 2),
    ('10021', 'Centre de démonstration Kara 1',       'KAR', 1),
    ('10022', 'Centre de démonstration Kara 2',       'KAR', 2),
    ('10031', 'Centre de démonstration Centrale 1',   'CEN', 1),
    ('10032', 'Centre de démonstration Centrale 2',   'CEN', 2),
    ('10041', 'Centre de démonstration Plateaux 1',   'PLA', 1),
    ('10042', 'Centre de démonstration Plateaux 2',   'PLA', 2),
    ('10051', 'Centre de démonstration Maritime 1',   'MAR', 1),
    ('10052', 'Centre de démonstration Maritime 2',   'MAR', 2),
    ('10061', 'Centre de démonstration Grand Lomé 1', 'GLO', 1),
    ('10062', 'Centre de démonstration Grand Lomé 2', 'GLO', 2)
) as c (code, nom, region, ordre)
join bi.zone r on r.code = c.region
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
