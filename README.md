# Calen7drier

## Développement

### Prérequis

- [Poetry](https://python-poetry.org/docs/#installation)

### Lancement

```bash
cp .env.example .env
nvim .env  # remplir les variables d'environnement
poetry install
poetry run flask --app ade_feed_url.server run --host 0.0.0.0 --port 5555
```
