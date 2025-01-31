# League of Legends Chatbot 🎮

Un chatbot intelligent spécialisé dans League of Legends, capable de répondre à vos questions sur les champions, leurs capacités et le jeu en général.

## 🌟 Fonctionnalités

- Informations détaillées sur les champions
- Description des capacités
- Réponses aux questions générales sur le jeu
- Interface web interactive

## 📁 Structure du Projet

```
lol-chatbot/
├── src/                      # Code source principal
│   ├── api/                  # Intégrations API (Riot, HuggingFace)
│   ├── chatbot/             # Logique du chatbot
│   ├── config/              # Configuration
│   ├── interface/           # Interface utilisateur
│   ├── models/              # Modèles de données
│   └── utils/               # Utilitaires
├── tests/                   # Tests unitaires et d'intégration
│   ├── unit/               # Tests unitaires
│   └── integration/        # Tests d'intégration
├── docs/                    # Documentation
├── .streamlit/             # Configuration Streamlit
├── .env.example            # Example de variables d'environnement
├── .env                    # Variables d'environnement (non versionné)
├── requirements.txt        # Dépendances Python
├── pytest.ini             # Configuration des tests
└── run.py                 # Script de lancement
```

## 🚀 Installation

1. Cloner le repository :

```bash
git clone https://github.com/votre-username/lol-chatbot.git
cd lol-chatbot
```

2. Créer un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :

```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

## 💻 Utilisation

1. Lancer l'interface web :

```bash
python run.py
```

2. Ouvrir dans le navigateur :

```
http://localhost:8501
```

## 🧪 Tests

Exécuter les tests :

```bash
pytest
```

## 📝 API Reference

### Riot Games API

- Documentation : https://developer.riotgames.com/
- Endpoints utilisés :
  - Champion Data
  - Game Data

### HuggingFace API

- Documentation : https://huggingface.co/docs/api-inference/
- Modèle utilisé : [Nom du modèle]

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m 'feat: add amazing feature'`)
4. Push la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📄 Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## 📧 Contact

Votre Nom - [@votre-twitter](https://twitter.com/votre-twitter)

Lien du projet : [https://github.com/votre-username/lol-chatbot](https://github.com/votre-username/lol-chatbot)
