# TP-MIXTE

## Lancer l'application avec Docker

Prérequis : Docker Desktop démarré.

Commande à lancer :

    docker compose up

Pour arréter les conteneurs :

    Ctrl+c
    docker compose down

| Service  | URL                           | Documentation          |
|----------|-------------------------------|------------------------|
| movie    | http://localhost:3001/graphql | movie/movie.yaml       |
| schedule | http://localhost:3002         | schedule/schedule.yaml |
| booking  | http://localhost:3003/graphql | booking/booking.yaml   |
| user     | http://localhost:3004         | user/user.yaml         |

`movie` et `booking` stockent leurs données dans MongoDB (consultable via
mongo-express sur http://localhost:8081). Ils se connectent à l'hôte `mongo` et se lancent donc avec Docker Compose.

## Comptes de test

| Rôle               | id            | password   |
|--------------------|---------------|------------|
| Administrateur     | `pam_beesly`  | `pam123`   |
| Utilisateur simple | `jim_halpert` | `jim123`   |

Pour se connecter, envoyer une requête `POST http://localhost:3004/login` avec le corps JSON :

    { "id": "<id>", "password": "<password>" }

Ajouter ensuite le `access_token` reçu à l'en-tête des requêtes protégées :

    Authorization: Bearer <access_token>
