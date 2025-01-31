# Documentation API

## Riot Games API

### Configuration

```python
RIOT_API_KEY=votre-clé-api
REGION=euw1
```

### Endpoints utilisés

#### Champion Data

- URL: `http://ddragon.leagueoflegends.com/cdn/{version}/data/{lang}/champion/{championName}.json`
- Méthode: GET
- Paramètres:
  - version: Version de l'API (ex: "13.24.1")
  - lang: Langue (ex: "fr_FR")
  - championName: Nom du champion en minuscules

#### Exemple de réponse

```json
{
  "type": "champion",
  "format": "standAloneComplex",
  "version": "13.24.1",
  "data": {
    "ahri": {
      "id": "Ahri",
      "key": "103",
      "name": "Ahri",
      "title": "La Renarde à Neuf Queues",
      "lore": "...",
      "spells": [
        {
          "id": "AhriQ",
          "name": "Orbe d'Illusion",
          "description": "..."
        }
      ]
    }
  }
}
```

## HuggingFace API

### Configuration

```python
HUGGINGFACE_API_KEY=votre-clé-api
HUGGINGFACE_MODEL_URL=https://api-inference.huggingface.co/models/votre-modèle
```

### Endpoints utilisés

#### Text Generation

- URL: `https://api-inference.huggingface.co/models/{model-id}`
- Méthode: POST
- Headers:
  - Authorization: "Bearer {api-key}"
- Body:

```json
{
  "inputs": "Votre texte ici"
}
```

#### Exemple de réponse

```json
[
  {
    "generated_text": "Réponse générée par le modèle"
  }
]
```

## Gestion des erreurs

### Codes d'erreur

- 200: Succès
- 400: Requête invalide
- 401: Non autorisé (clé API invalide)
- 404: Ressource non trouvée
- 429: Trop de requêtes
- 500: Erreur serveur

### Exemple de gestion

```python
try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur {response.status_code}: {response.text}")
        return None
except Exception as e:
    print(f"Erreur: {str(e)}")
    return None
```
