# UE-AD-A1-MIXTE

## Lancer l'application avec Docker

Prérequis : Docker Desktop démarré. Au premier lancement, les images (dont
MongoDB) sont téléchargées automatiquement, ce qui demande une connexion Internet.
Les commandes se lancent depuis la racine du projet.

    docker compose up --build -d     # construit les images et lance les conteneurs
    docker compose logs -f           # suit les logs
    docker compose down              # arrête et supprime les conteneurs
    docker compose down -v           # idem, et réinitialise les données

| Service  | URL                           | Documentation          |
|----------|-------------------------------|------------------------|
| movie    | http://localhost:3001/graphql | movie/movie.yaml       |
| schedule | http://localhost:3002         | schedule/schedule.yaml |
| booking  | http://localhost:3003/graphql | booking/booking.yaml   |
| user     | http://localhost:3004         | user/user.yaml         |

`movie` et `booking` stockent leurs données dans MongoDB (consultable via
mongo-express sur http://localhost:8081). Ils se connectent à l'hôte `mongo` :
ils se lancent donc avec Docker Compose.
