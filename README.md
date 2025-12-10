# chatbot_univ-lille

Courte description
- Chat bot univ lille RAG.

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

## Frontend (React)

Un frontend minimal en React est disponible dans le dossier `frontend/`. Il communique avec l'API via l'endpoint `POST /chat`.

Instructions rapides :
```bash
cd frontend
npm install
npm run dev
```

Le frontend appelle par défaut `http://localhost:8000/chat`. Pour changer l'URL du backend :
```bash
VITE_API_URL="http://localhost:8000" npm run dev
```

## Pipeline RAG (résumé)
- Préparer/cleaner les données dans `data/`.
- Découper les textes en chunks (LangChain `RecursiveCharacterTextSplitter`).
- Générer les embeddings localement avec `nomic-embed-text` via Ollama.
- Indexer les chunks et embeddings dans ChromaDB.
- Construire un pipeline retrieval+generation : rechercher top_k chunks, construire le prompt, appeler Ollama et renvoyer la réponse.

Voir les scripts proposés dans `tools/` (à créer) pour automatiser ces étapes.