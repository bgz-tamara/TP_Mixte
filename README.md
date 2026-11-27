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
