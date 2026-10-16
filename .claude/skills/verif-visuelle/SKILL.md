---
name: verif-visuelle
description: Compare le rendu d'une page de l'application à la maquette validée, aux largeurs 1 440, 1 000 et 390 px, et vérifie l'accessibilité. À utiliser après toute modification visible d'une page ou d'un composant.
argument-hint: "<chemin de la page, ex. /enrolement>"
---

# Vérification visuelle : $ARGUMENTS

1. Vérifier que le front tourne (`npm run dev` dans `frontend/`, port 5173). Le backend en profil dev donne des données ;
   sans lui, le script simule `/api/v1/meta` seulement.
2. Prendre les captures :
   `cd frontend && node e2e/outils/captures.mjs $ARGUMENTS`
   Le script écrit `frontend/test-results/captures/<page>-<largeur>.png` (1 440, 1 000, 390 px, page entière).
3. Lire (outil Read) chaque capture et la capture de maquette correspondante dans `maquette/captures/`
   (`<Maquette>-1440.png`, `<Maquette>-390.png` ; le nom de la maquette est dans `frontend/src/pages/pages.ts`).
4. Comparer et lister les écarts, du plus visible au moins visible :
   - ordre et présence des blocs, libellés exacts, chiffres et unités ;
   - couleurs (seulement les jetons de `jetons.css`), tailles de texte, alignements, espacements ;
   - comportement mobile (menu, filtres, tableaux réduits aux colonnes clés, pas de défilement horizontal).
5. Lancer `npm run test:e2e` : aucune violation axe (WCAG 2.1 AA) n'est acceptée.
6. Corriger les écarts qui relèvent de l'application. Si un écart vient d'un choix volontaire (donnée réelle différente
   de la donnée de test de la maquette, par exemple), le dire dans la réponse au lieu de le « corriger ».
