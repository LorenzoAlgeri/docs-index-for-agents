# API

| Method | Path | Purpose |
|---|---|---|
| GET | /t/{tenant}/recipes | list recipes, newest first |
| POST | /t/{tenant}/recipes | create a recipe |
| GET | /t/{tenant}/recipes/{id} | read one recipe |
| POST | /t/{tenant}/follow/{cook} | follow a cook |
| GET | /t/{tenant}/shopping-list.csv | export the weekly list |

Errors use plain status codes and a JSON body with a `reason` field.
