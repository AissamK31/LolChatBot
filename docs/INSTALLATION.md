# Guide d'Installation

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git
- Compte Riot Games Developer
- Compte HuggingFace

## Installation pas à pas

### 1. Cloner le repository

```bash
git clone https://github.com/votre-username/lol-chatbot.git
cd lol-chatbot
```

### 2. Environnement virtuel

#### Sur Linux/MacOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Sur Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration des API

1. Créer un compte sur [Riot Developer Portal](https://developer.riotgames.com/)
2. Créer un compte sur [HuggingFace](https://huggingface.co/)
3. Copier le fichier d'exemple :

```bash
cp .env.example .env
```

4. Éditer `.env` avec vos clés API :

```env
RIOT_API_KEY=votre-clé-riot
HUGGINGFACE_API_KEY=votre-clé-huggingface
REGION=euw1
```

### 5. Vérification de l'installation

1. Lancer les tests :

```bash
pytest
```

2. Lancer l'interface web :

```bash
python run.py
```

3. Ouvrir dans le navigateur :

```
http://localhost:8501
```

## Résolution des problèmes courants

### Erreur : "ModuleNotFoundError"

- Vérifier que l'environnement virtuel est activé
- Réinstaller les dépendances : `pip install -r requirements.txt`

### Erreur : "API key not found"

- Vérifier que le fichier `.env` existe
- Vérifier que les clés API sont correctement renseignées

### Erreur : "Connection refused"

- Vérifier que le port 8501 n'est pas utilisé
- Essayer un autre port : `python run.py --server.port=8502`

### Erreur NLTK

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Support

En cas de problème :

1. Consulter les [Issues GitHub](https://github.com/votre-username/lol-chatbot/issues)
2. Créer une nouvelle issue avec :
   - Description détaillée du problème
   - Logs d'erreur
   - Environnement (OS, version Python)
