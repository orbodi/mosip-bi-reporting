# Charte et jetons de design

Valeurs relevées sur la maquette (version 92 du canvas, 9 oct. 2026) et rationalisées. Le code n'utilise que les
variables CSS de `frontend/src/styles/jetons.css` ; aucune couleur ni taille en dur dans les composants.

## Couleurs
| Jeton | Valeur | Usage |
|---|---|---|
| `--bleu` | `#1F4E8C` | marque : bandeau du titre, pied de page, liens, chiffres en bleu |
| `--bleu-pastille` | `#2D5E9E` | pastilles de filtre sur le bandeau |
| `--bleu-clair` | `#E3EAF3` | fonds d'accent (avatar, survol) |
| `--or` | `#FCBA21` | jaune ANID : onglet actif, crochets de l'élément principal, pastille de mise à jour |
| `--or-texte` | `#B07D00` | icônes d'alerte jaunes sur fond blanc (3,6:1, éléments graphiques) |
| `--or-pale` | `#FEF4DC` | encadré du chiffre clé |
| `--encre` | `#071B35` | texte principal, titres |
| `--encre-2` | `#4B5A6E` | texte secondaire, libellés |
| `--trait` | `#E6EBF0` | filets, séparateurs |
| `--bord-champ` | `#7F8C9D` | bordures des champs (3,4:1) |
| `--fond` | `#F1F4F6` | fond de page |
| `--surface` | `#FFFFFF` | panneaux et cartes |
| `--danger` | `#D03B3B` | échecs, rejets |
| `--succes` | `#1BAF7A` | réussites |

Data-viz (validées avec le validateur du skill dataviz pendant la maquette) :
- séries : `#2A78D6` (principale), `#1BAF7A` (seconde), `#D03B3B` (échecs) ; hommes `#0E8A62`, femmes `#2A78D6` ;
- chevrons du parcours : `#2368C2` en alternance avec `--bleu` ;
- échelle séquentielle (carte) : `#B7D3F6`, `#6DA7EC`, `#2A78D6`, `#184F95` ; dégradé ordonné `#86B6EF` → `#104281`.
- Une couleur fixe par indicateur d'une page à l'autre (ex. NIU toujours en bleu marine).

## Typographie
Poppins (auto-hébergée via `@fontsource/poppins`, pas de CDN), chiffres tabulaires pour les valeurs.

| Jeton | Taille | Usage |
|---|---|---|
| `--t-xs` | 12px | notes, légendes, axes |
| `--t-s` | 13px | libellés, textes secondaires |
| `--t-m` | 14px | texte courant, tableaux |
| `--t-l` | 16px | sous-titres de blocs |
| `--t-xl` | 20px | titres de blocs (h2) |
| `--t-2xl` | 22px | titres de sections principales |
| `--t-titre` | 30px | titre de page dans le bandeau (h1) |
| `--t-kpi` | 26px | valeur des cartes KPI |
| `--t-hero` | 38px | chiffre clé de la page (30px sous 700 px) |

La maquette utilise encore 21 tailles différentes (12,5 / 13,5 / 11,5 px…) : les ramener à cette échelle au développement.

## Formes
- Rayons : `--r-s` 4px (champs), `--r-m` 8px (boutons, cellules), `--r-l` 14px (panneaux), `--r-pilule` 999px.
- Ombres : `--ombre-1` `0 2px 6px rgba(7,27,53,.06)` (cartes), `--ombre-2` `0 1px 2px rgba(7,27,53,.06), 0 8px 24px rgba(7,27,53,.06)` (panneaux), `--ombre-3` `0 14px 34px rgba(7,27,53,.18)` (menus).
- Espacements : multiples de 4px (`--e-1` 4px … `--e-8` 32px).

## Mise en page
- Largeur de contenu 1 248px max ; gouttières 32px, 16px sous 700 px.
- Bandeau bleu avec empreinte décorative à droite (`maquette/assets/bande-empreintes-v3.svg`) ; le premier panneau le chevauche.
- Points de rupture : 1 340 (frise complète), 1 100, 1 000, 900 (paires de panneaux côte à côte jusqu'ici), 700 (mobile).
