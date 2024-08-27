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

## Déploiement

### Prérequis

- Avoir `docker` installé
- Avoir [Fish](https://fishshell.com/) installé (déso pas déso mdrrrr)
- Avoir les accès sur harbor.k8s.inpt.fr/net7

### Pour release une nouvelle version

1. Modifier le numéro de version en haut de `push.fish`
1. Faire un commit taggé avec `vVERSION` (ex: `v0.1.0`)

### Lanchement

```bash
fish push.fish
```
