# Dictionnaire des indicateurs

Source de vérité pour chaque chiffre affiché. Un indicateur n'entre dans le code qu'avec sa fiche complète.
Les sources MOSIP sont **probables** tant que le statut n'est pas « validé » (à confirmer avec l'équipe MOSIP de l'ANID).

Les valeurs de référence sont celles du BI actuel au 14/01/2026 (dernière donnée d'enrôlement). Elles servent de tests
de non-régression sur un instantané des données : le nouveau BI doit les retrouver, ou expliquer l'écart ici.
« Test » = valeur de la maquette, pas une donnée réelle.

## Dimensions communes
| Dimension | Valeurs | Source probable |
|---|---|---|
| Territoire | Togo → région (6) → préfecture (39 officielles ; 37 dans geoBoundaries) → commune → canton → localité → centre (CSC) → machine | `master.location`, `master.registration_center` ; centre et machine lus dans le RID (5 + 5 premiers chiffres) |
| Temps | jour, semaine (lundi), mois, année | horodatages des tables sources |
| Sexe | Femmes, Hommes | à décider : pas de `anonymous_profile` en MOSIP 1.1.5 (voir `docs/decisions.md`) ; « inconnu » en attendant |
| Tranche d'âge | 0-5, 6-14, 15-18, 19-25, > 25 (ordre numérique, jamais alphabétique) | à décider, comme le sexe |
| Type de demande | 8 types (nouvelle inscription ≈ 99 %, mise à jour, perte…) | `registration.reg_type` |
| Statut du paquet | 9 statuts MOSIP regroupés (règle à valider) | `status_code` / `latest_trn_status_code`, regroupés par `pipeline.correspondance_statut` |

## Enrôlement
| Code | Indicateur | Définition et calcul | Source probable | Référence | Statut |
|---|---|---|---|---|---|
| E-PRE | Pré-inscriptions | demandes de pré-inscription créées | `mosip_prereg.applicant_demographic` (données d'identité : exclue de la capture ; autre source ou dérogation à décider) | 606 850 | à confirmer |
| E-PRE-RDV | Rendez-vous réservés | pré-inscriptions avec rendez-vous ; le BI actuel affiche 0 (anomalie) | `mosip_prereg.reg_appointment` | ≈ 546 964 | à confirmer |
| E-INS | Inscriptions | paquets d'inscription reçus | `mosip_regprc.registration` | 3 278 239 | à confirmer |
| E-NIU | NIU générés | inscriptions abouties avec NIU ; % = NIU / inscriptions | `registration` traitée (NEW) ; `mosip_idrepo.uin` exclue de la capture (NIU, données d'identité) sauf dérogation | 3 058 886 (93,3 %) | à confirmer |
| E-COURS | En cours | inscriptions ni abouties, ni échouées, ni rejetées | `registration` | 123 639 | à confirmer |
| E-BLOQ | Bloquées depuis plus de 30 jours | en cours dont la dernière transaction a plus de 30 jours | `registration_transaction` | 118 402 | à confirmer |
| E-ECH | Échouées | traitement en échec technique | `registration` | 9 218 | test (répartition) |
| E-REJ | Rejetées | `status_code = REJECTED` ; taux = rejets / inscriptions | `registration` | 86 496 (2,6 %) | à confirmer |
| E-TRAIT | Paquets traités | NIU + échouées + rejetées | calcul | 3 154 600 | validé (maquette) |
| E-MAJ | Mises à jour | `reg_type` UPDATE (et RES_UPDATE ?) | `registration` | 12 689 | à confirmer |
| E-PERTE | Récupérations de NIU | `reg_type` LOST | `registration` | 2 051 | à confirmer |
| E-DELAI | Délai médian inscription → NIU | médiane (date NIU − date d'inscription), en jours | `registration` (date du NIU sans `uin` : à définir) | 6,5 j | test |

Contrôle : pour chaque zone et chaque période, NIU + rejetées + échouées + en cours (+ non classées) = inscriptions.

Mise en œuvre temps réel (16/10/2026, bloc « Devenir des inscriptions », `GET /api/v1/enrolement/devenir`) :
`bi.fait_enrolement_jour` est recalculé en continu depuis `etat.registration` (pipeline CDC, `pipeline/README.md`).
Règles provisoires, à confirmer avec l'équipe MOSIP :
- jour d'une inscription = `cr_dtimes` (réception par MOSIP) ;
- exclues : inscriptions supprimées dans MOSIP et `is_deleted = true` ;
- statut regroupé par `pipeline.correspondance_statut` ; un code absent compte en « non classées », affichées à part ;
- « NIU générés » = inscriptions abouties de tous types de demande (NEW ≈ 99 %) ; restreindre à NEW si l'équipe MOSIP
  le demande ;
- E-BLOQ (bloquées depuis plus de 30 jours) n'est pas encore calculé : c'est un stock daté, pas un fait par jour.

## Impression des cartes
| Code | Indicateur | Définition et calcul | Source probable | Référence | Statut |
|---|---|---|---|---|---|
| I-DEM | Demandes d'impression | demandes de carte envoyées | `mosip_credential.credential_transaction` | 3 113 431 | à confirmer |
| I-ATT | Demandes en attente | demandes non encore imprimées | idem | 11 835 | à confirmer |
| I-REJ | Demandes rejetées | demandes refusées (dernière le 13/03/2026 : anomalie) | idem | 6 | à confirmer |
| I-EXP | Cartes imprimées et expédiées | cartes sorties de l'imprimeur | idem + partenaire d'impression | 3 101 590 | à confirmer |
| I-REM | Cartes remises | cartes remises au citoyen ; % des expédiées et % des inscrits | partenaire de distribution (hors MOSIP) | 1 770 796 (57,1 % ; 54,0 %) | à confirmer |
| I-AREM | Cartes à remettre | expédiées − remises | calcul | 1 330 794 | validé (maquette) |
| I-DELAI | Délai du NIU à la carte remise | médiane en jours | à créer | 34 j | test |

Anomalie connue : demandes (3 113 431) > NIU (3 058 886), écart 54 545 à réconcilier.

## ABIS (journaux IN Groupe, voir docs/sources-mosip.md)
| Code | Indicateur | Règle (document IN Groupe v0.2) | Référence | Statut |
|---|---|---|---|---|
| AB-INS | Requêtes d'insertion | `mosip.abis.insert`, activité START | 3 159 591 | test |
| AB-DED | Requêtes de déduplication | `mosip.abis.identify`, activité START | 3 158 734 | test |
| AJ-REC | Requêtes d'adjudication reçues | `mosip.manual.adjudication.adjudicate`, START | 41 870 | test |
| AJ-TRT | Cas traités | réponse publiée, `returnValue = 1` | 39 205 | test |
| AJ-HIT / AJ-NOHIT | HIT / NO HIT | dossiers traités avec `candidateList.count > 0` / `= 0` | 16 002 / 23 203 | test |
| AJ-ATT | Dossiers en attente | reçues − traitées − en erreur | 2 353 | test |
| AB-ERR | Erreurs ABIS | réponse publiée, `returnValue = 2`, par service | 2 273 (857 / 1 104 / 312) | test |
| SB-* | Qualité Face, Iris, Fingerprint | moyenne des scores des lignes `RqType=IP` (MBSS) | 212,3 / 80,3 / 99,8 | test |
| SB-EXPL | Doigts exploitables | NBPK ≥ 16 (hypothèse : NBPK = minuties, à confirmer) | 95,5 % | test |

Le BI actuel ne montre que 995 insertions et 1 236 déduplications (une journée, 13/07/2026) : collecte des journaux à vérifier.

## IDPS
| Code | Indicateur | Définition | Référence | Statut |
|---|---|---|---|---|
| ID-ORD | Ordres reçus depuis MOSIP | ordres d'impression reçus par l'IDPS | 14 | à confirmer |
| ID-ATT | En attente | ordres non imprimés | 14 | à confirmer |
| ID-IMP | Cartes imprimées | ordres aboutis | 0 | à confirmer |
| ID-ERR | Erreurs | par étape : personnalisation 3, contrôle qualité 5, supervision 6 | 14 | à confirmer |
| ID-ECHEC | Taux d'échec | ordres en erreur / ordres reçus | 100 % | à confirmer |

## Authentifications
| Code | Indicateur | Définition | Source probable | Référence | Statut |
|---|---|---|---|---|---|
| A-REQ | Requêtes | demandes d'authentification reçues | `mosip_ida.auth_transaction` | 510 499 | à confirmer |
| A-OK | Réussies | statut succès ; % des requêtes | idem | 215 736 (42,3 %) | à confirmer |
| A-KO | Échouées | statut échec | idem | 294 763 (57,7 %) | à confirmer |
| A-TYPE | Par type | BIO 490 080 ; OTP 18 380 ; DEMO et MULTIPLE 2 039 | idem | — | à confirmer |
| A-CAUSE | Causes d'échec | codes d'erreur IDA (à exposer) | idem | — | à créer |
| A-PART | Partenaires raccordés | partenaires ayant au moins une requête | `mosip_pms.partner` | 1 (Atos) | à confirmer |

## Modèle de fiche (copier pour un nouvel indicateur)
```
### CODE : Libellé exact de la maquette
- Définition : ce que l'on compte, en une phrase.
- Calcul : formule ou requête de référence (table, colonnes, filtres).
- Dénominateur (si %) : ...
- Source : table ou journal ; fraîcheur attendue.
- Axes : territoire / temps / sexe / âge / type / autre.
- Pages : où il apparaît.
- Référence : valeur connue et date.
- Contrôles : égalités qui doivent tenir (ex. somme des statuts = total).
- Statut : à confirmer | validé | test.
```
