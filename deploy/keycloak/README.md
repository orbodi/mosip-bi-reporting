# Keycloak de développement

Realm `anid` importé au démarrage (`realm-anid-dev.json`), client public `bi-reporting` (code + PKCE).
**Comptes de test, uniquement pour le poste de développement** :

| Identifiant | Mot de passe | Rôle |
|---|---|---|
| national.test | dev-bi-national | bi-national |
| savanes.test | dev-bi-savanes | bi-regional |

Console d'administration : http://localhost:8180 (admin / admin, développement).

À faire avant de tester la portée régionale : déclarer l'attribut utilisateur `zone` dans le profil utilisateur du realm
(Realm settings > User profile), lui donner la valeur `SAV` pour `savanes.test`, et ajouter un mapper
« User Attribute » `zone` sur le client `bi-reporting` pour le mettre dans le jeton. Exporter ensuite le realm ici.

En recette et en production, on utilise le Keycloak de MOSIP (realm de l'ANID) : ce fichier ne sert pas.
