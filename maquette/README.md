# Maquette validée (référence visuelle, ne pas modifier)

Maquette du BI Reporting validée en octobre 2026 (version 92 du canvas Design, 9 oct. 2026). L'application doit la
reproduire ; un écart volontaire se décide et s'écrit dans `docs/decisions.md`.

| Dossier | Contenu |
|---|---|
| `presentation/` | `BI_ANID_maquette_presentation.html` : les 7 pages interactives dans un seul fichier, à ouvrir dans un navigateur (écran de connexion fictif : n'importe quel identifiant). |
| `captures/` | Captures pleine page à 1 440 et 390 px : `<Page>-1440.png`, `<Page>-390.png`. Point de comparaison de `/verif-visuelle`. |
| `pages/` | Sources des pages (format du canvas Design) : valeurs exactes de CSS, libellés, structure des blocs. |
| `assets/` | Logo ANID, bandeau à empreinte, fond de la carte du Togo. |
| `generateur/` | Scripts Python qui ont produit la maquette (historique ; chemins à adapter, non maintenus). |

Correspondance pages ↔ onglets : `Main` Vue d'ensemble, `Enrolement` Enrôlement, `Cartes` Impression des cartes,
`Biometrie` ABIS, `Idps` IDPS, `Usage` Authentifications, `Technique` Exploration.

Attention : une partie des chiffres de la maquette sont des **données de test** (toute la page ABIS, répartitions
détaillées, séries journalières). Les valeurs réelles de référence sont dans `docs/indicateurs.md`.

Le hook `proteger.mjs` bloque toute modification de ce dossier par Claude Code
(sauf avec `BI_MAQUETTE_MODIFIABLE=1`, pour intégrer une nouvelle version validée).
