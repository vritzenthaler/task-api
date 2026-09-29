# Task API

API de gestion de tâches avec FastAPI, SQLite, bcrypt et authentification JWT RS256. Chaque utilisateur accède uniquement à ses propres tâches.

## Installation

Python 3.10 minimum (développement avec Python 3.12) et `uv`. Depuis la racine du projet :

```bash
uv sync --extra dev --locked
uv run python scripts/setup_local.py
uv run uvicorn app.main:app --reload
```

Le script crée une nouvelle paire de clés RSA dans `.keys/` et une phrase secrète aléatoire dans `.env`. Il refuse de remplacer une configuration existante. `.env.example` décrit la variable utilisée. Aucun compte, aucune clé et aucune base de données ne sont livrés avec le projet.

SQLite crée `app_database.db` au démarrage. Documentation interactive : http://127.0.0.1:8000/docs.

## Utilisation

1. Créer un compte avec `POST /users/register`, par exemple `{"username": "alice", "password": "your-password"}`.
2. Se connecter avec `POST /users/login` et les mêmes identifiants.
3. Fournir `access_token` dans `Authorization: Bearer <token>`. Dans `/docs`, utiliser **Authorize**.

Les jetons expirent après 15 minutes. Les noms d'utilisateur et les titres acceptent de 1 à 16 lettres ASCII, sans espace ni chiffre.

| Méthode | Route | Fonction |
| --- | --- | --- |
| POST | `/users/register` | Inscription |
| POST | `/users/login` | Connexion |
| GET | `/tasks` | Liste des tâches |
| POST | `/tasks` | Création avec `{"title": "Example"}` |
| GET | `/tasks/{task_id}` | Consultation |
| PATCH | `/tasks/{task_id}` | Modification de `title` et/ou `done` |
| DELETE | `/tasks/{task_id}` | Suppression |

## Tests

```bash
uv run --extra dev pytest
```

Les tests génèrent une base SQLite et des clés JWT temporaires. Ils fonctionnent sans `.env` ni configuration locale préalable.

## Dépendances

`pyproject.toml` déclare les dépendances ; `uv.lock` verrouille leurs versions. Après une modification, lancer `uv lock`. Aucun `requirements.txt` séparé n'est maintenu.

## Nouveau dépôt

Git est initialisé sur `main`, sans historique importé et sans remote. Après création d'un dépôt distant vide :

```bash
git add .
git commit -m "Initial Task API extraction"
git remote add origin <URL_DU_DEPOT>
git push -u origin main
```

Les secrets, clés, bases locales, environnements virtuels et caches sont exclus par `.gitignore`.
