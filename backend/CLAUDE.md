# Backend (API Spring Boot)

Java 21, Spring Boot 4.1, Maven. Package racine `tg.anid.bi`, découpé par domaine (`meta`, `enrolement`, `cartes`,
`abis`, `idps`, `authentifications`, `exploration`) plus `config` et `commun`.

## Conventions
- Une ressource REST par bloc de page, sous `/api/v1/<domaine>/...`, en lecture seule (GET).
- DTO en `record` Java ; noms métier en français (`inscriptions`, `niuGeneres`), comme dans `docs/indicateurs.md`.
- Accès aux données avec `JdbcClient` et du SQL lisible dans des blocs de texte. Pas de JPA : l'API lit des tables
  agrégées, le SQL explicite se relit et se teste mieux.
- Contrôleur fin ; la logique (bornes de période, portée de zone, calculs de taux) va dans un service testé.
- Paramètres communs : `du` et `au` (`LocalDate`, bornés aux données disponibles), `zone` (code). Valider avec Bean Validation.
- Réponses : nombres bruts, jamais de texte formaté ni de pourcentage arrondi pour l'affichage.
- Erreurs : `ProblemDetail` (voir `commun/GestionErreurs`).
- Accès : chaque utilisateur lit tout le Togo, sans restriction de zone (décision du 25/10/2026). Le paramètre `zone`
  accepte un code de tout niveau (région à centre).
- Migrations Flyway dans `src/main/resources/db/migration`, en ajout seulement (`V2__...`, `V3__...`).
  Données de démonstration dans `db/dev` (profil dev).

## Tests
- Unitaires (`*Test.java`, `mvn test`) : JUnit 5, AssertJ, Mockito ; contrôleurs testés avec MockMvc en mode standalone.
- Intégration (`*IT.java`, `mvn verify`) : `@SpringBootTest` sur PostgreSQL Testcontainers (URL `jdbc:tc:`), Docker requis.
- Toute requête SQL d'agrégat a un test d'intégration qui vérifie au moins un total et une égalité de contrôle
  (ex. NIU + rejetées + échouées + en cours = inscriptions).

## Commandes
- `mvn spring-boot:run -Dspring-boot.run.profiles=dev` : API sur http://localhost:8080 (Swagger : /swagger-ui.html)
- `mvn spring-boot:run -Dspring-boot.run.profiles=dev,demo` : en plus, deux ans d'inscriptions fictives pour la page
  Enrôlement (`db/demo`) ; base vide ou déjà en démonstration, jamais avec la chaîne temps réel
- `mvn test` puis `mvn verify` avant de rendre la main quand le backend a changé.
