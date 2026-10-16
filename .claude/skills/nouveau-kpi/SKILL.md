---
name: nouveau-kpi
description: Ajoute ou modifie un indicateur du BI de bout en bout (fiche du dictionnaire, modèle dbt, API, composant, tests). À utiliser dès qu'un chiffre nouveau ou modifié doit apparaître sur une page.
argument-hint: "<code ou libellé de l'indicateur> [page]"
---

# Nouvel indicateur : $ARGUMENTS

Suivre les étapes dans l'ordre. Ne pas passer à l'étape suivante tant que la précédente n'est pas vérifiée.

## 1. Fiche du dictionnaire
- Chercher l'indicateur dans `docs/indicateurs.md`. S'il manque, ajouter sa fiche avec le modèle en bas du fichier :
  définition, calcul, dénominateur, source, axes, pages, référence, contrôles, statut.
- Si la source MOSIP ou le calcul est incertain, garder le statut « à confirmer » et poser la question à l'humain
  plutôt que de deviner une colonne.
- Relever le libellé exact et la présentation dans la page de maquette (`maquette/pages/<Page>.dc.html`,
  `maquette/captures/<Page>-1440.png`).

## 2. Données (pipeline)
- Modèle dbt dans `pipeline/models/` (staging puis marts) qui alimente la table `bi.*` concernée.
- Test dbt pour chaque égalité de contrôle de la fiche (ex. NIU + rejetées + échouées + en cours = inscriptions).
- Si la table `bi.*` change : nouvelle migration Flyway `V<n+1>__....sql` (jamais modifier une migration existante).

## 3. API (backend)
- Record de réponse, requête SQL avec `JdbcClient` (filtres `du`, `au`, `zone`), service, contrôleur sous `/api/v1/...`.
- Tests : unitaire du contrôleur (MockMvc standalone) et test d'intégration `*IT` qui vérifie un total et une égalité
  de contrôle sur des données de test, plus le refus d'une zone hors portée pour un utilisateur régional.

## 4. Front
- `npm run api:types` (backend démarré) pour régénérer `src/api/schema.ts`.
- Hook TanStack Query dans `src/api/<domaine>.ts`, composant dans la page, formats de `lib/format.ts`.
- Test Vitest du composant (valeurs formatées, état vide, état d'erreur).

## 5. Vérification
- `mvn verify` (backend) et `npm run lint && npm run typecheck && npm test` (front).
- `/verif-visuelle <page>` pour comparer à la maquette.
- Demander à l'agent `auditeur-donnees` de vérifier la concordance du chiffre entre dictionnaire, SQL, API et page.
- Mettre à jour le statut de la fiche et, si une anomalie apparaît, la consigner dans `docs/decisions.md`.
