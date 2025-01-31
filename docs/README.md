# Documentation du Chatbot LoL

## Structure du Projet

```
projet/
├── docs/                  # Documentation
├── src/                   # Code source
│   ├── api/              # Intégrations API
│   ├── chatbot/          # Logique du chatbot
│   ├── config/           # Configuration
│   ├── models/           # Modèles de données
│   └── utils/            # Utilitaires
├── tests/                # Tests
│   ├── unit/            # Tests unitaires
│   └── integration/     # Tests d'intégration
└── main.py              # Point d'entrée
```

## Installation

1. Créer un environnement virtuel :

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :

- Copier `.env.example` vers `.env`
- Remplir les clés API requises

## Utilisation

1. Lancer le chatbot :

```bash
python main.py
```

2. Commandes disponibles :

- Questions sur les champions
- Questions sur le jeu
- Tapez 'quit' pour quitter

## Tests

Exécuter les tests :

```bash
pytest tests/
```

## API Utilisées

- Riot Games API : Données LoL
- HuggingFace : Traitement du langage naturel
