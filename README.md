# chatbot_univ-lille

Courte description
- Petit projet pour collecter/extraire du contenu web (ex. scraper pour la page d'information de l'université).

## Structure du projet (proposée)
```
chatbot_univ-lille/
├─ .gitignore         # ignorer .venv/, etc.
├─ README.md
├─ requirements.txt
├─ scraper/
│  ├─ scraper.py
├─ data/               # fichiers/stocks de données récupérées
├─ notebooks/          # notebooks d'exploration
├─ tests/              # tests unitaires (pytest)
└─ docs/               # documentation complémentaire
```

## Prérequis
- Linux
- Python 3.8+
- pip
- (optionnel) virtualenv/venv

## Installation rapide
```bash
cd /home/utilisateur/Documents/chatbot_univ-lille
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Si `requirements.txt` n'existe pas :
```bash
pip install requests beautifulsoup4
pip freeze > requirements.txt
```

## Exécution
Depuis la racine du projet :
```bash
source .venv/bin/activate
python3 scraper/scraper.py
```

## Tests
Installer pytest puis lancer :
```bash
pip install pytest
pytest
```

## Bonnes pratiques / conseils
- Ajouter `.venv/` dans `.gitignore`.
- Ne pas committer les données sensibles / gros fichiers ; utiliser `data/` ignoré si nécessaire.
- Documenter les variables de configuration (URL, délais, user-agent) dans un fichier `config.example.json` ou `.env`.
- Ajouter des tests unitaires pour la logique de parsing et mocker les requêtes HTTP.

## Contribution
- Ouvrir une issue puis un merge request.
- Respecter les conventions de code et ajouter des tests pour les changements importants.

## Licence & contact
- Indiquer la licence (ex. MIT) et une adresse de contact ou référent du projet.