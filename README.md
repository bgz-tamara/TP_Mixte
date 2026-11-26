# UE-AD-A1-MIXTE

## Lancer l'application avec Docker

    docker compose up --build -d     # construit les images et lance les conteneurs
    docker compose logs -f           # suit les logs
    docker compose down              # arrête et supprime les conteneurs
    docker compose down -v           # idem, et réinitialise les données

| Service  | URL                           | Documentation          |
|----------|-------------------------------|------------------------|
| movie    | http://localhost:3001/graphql | (à venir)              |
| schedule | http://localhost:3002         | schedule/schedule.yaml |
| booking  | http://localhost:3003/graphql | booking/booking.yaml   |
| user     | http://localhost:3004         | user/user.yaml         |
