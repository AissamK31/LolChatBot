"""
API HuggingFace pour le chatbot League of Legends.
"""
import requests
import json
from typing import Optional, Dict, Any
from src.config.config import Config
from src.api.riot_api import RiotAPI

class HuggingFaceAPI:
    def __init__(self):
        """Initialisation de l'API HuggingFace"""
        self.config = Config()
        self.riot_api = RiotAPI()
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.headers = {
            "Authorization": f"Bearer {self.config.HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Prompt système pour guider le modèle
        self.system_prompt = """Tu es un expert de League of Legends qui répond exclusivement en français.
Tu as accès aux données en temps réel du jeu via l'API Riot.

Tu dois fournir des informations précises et détaillées sur :
- Les champions (capacités, statistiques, stratégies)
- Les mécaniques de jeu
- Les builds et objets
- Les matchups et contre-picks
- Les stratégies de jeu

Règles importantes :
1. Réponds TOUJOURS en français
2. Sois précis et concis
3. Base tes réponses UNIQUEMENT sur les données fournies par l'API Riot
4. Adapte tes conseils au niveau du joueur (débutant, intermédiaire, expert)
5. Si tu n'as pas l'information dans les données fournies, dis-le clairement
6. Utilise la terminologie officielle du jeu

Format des réponses :
- Pour les champions : utilise les statistiques et capacités exactes
- Pour les capacités : utilise les valeurs précises de l'API
- Pour les builds : base-toi sur les données actuelles
- Pour les matchups : analyse avec les statistiques fournies

N'invente JAMAIS d'informations. Utilise UNIQUEMENT les données fournies."""

    def _enrich_context_with_riot_data(self, query: str) -> Dict[str, Any]:
        """Enrichit le contexte avec les données de l'API Riot"""
        context = {}
        
        # Extraire les mots clés de la requête
        keywords = query.lower().split()
        
        # Rechercher des informations sur les champions mentionnés
        for word in keywords:
            champion_info = self.riot_api.get_champion_info(word)
            if champion_info:
                context['champion'] = champion_info
                # Récupérer les statistiques enrichies
                if 'stats' in champion_info:
                    context['champion_stats'] = champion_info['stats']
                # Récupérer les capacités
                if 'abilities' in champion_info:
                    context['abilities'] = champion_info['abilities']
                # Récupérer les matchups si un rôle est spécifié
                for role in ['top', 'jungle', 'mid', 'bot', 'support']:
                    if role in keywords:
                        matchups = self.riot_api.get_champion_matchups(word, role)
                        if matchups:
                            context['matchups'] = matchups
                        break
        
        return context

    def _format_riot_data_for_prompt(self, context: Dict[str, Any]) -> str:
        """Formate les données Riot pour le prompt"""
        if not context:
            return ""
            
        formatted_data = "\nDonnées Riot actuelles :\n"
        
        if 'champion' in context:
            champion = context['champion']
            formatted_data += f"\nChampion : {champion['name']}\n"
            formatted_data += f"Rôles : {', '.join(champion.get('tags', []))}\n"
            
            if 'stats' in context['champion']:
                stats = context['champion']['stats']
                formatted_data += "\nStatistiques de base :\n"
                formatted_data += f"- PV : {stats['hp']} (+{stats['hpperlevel']})\n"
                formatted_data += f"- Dégâts : {stats['attackdamage']} (+{stats['attackdamageperlevel']})\n"
                formatted_data += f"- Armure : {stats['armor']} (+{stats['armorperlevel']})\n"
            
            if 'abilities' in context:
                abilities = context['abilities']
                formatted_data += "\nCapacités :\n"
                if 'passive' in abilities:
                    formatted_data += f"Passif - {abilities['passive']['name']}\n"
                if 'spells' in abilities:
                    for i, spell in enumerate(['Q', 'W', 'E', 'R']):
                        if i < len(abilities['spells']):
                            formatted_data += f"{spell} - {abilities['spells'][i]['name']}\n"
            
            if 'matchups' in context:
                matchups = context['matchups']
                formatted_data += "\nMatchups :\n"
                if 'counter_picks' in matchups:
                    formatted_data += f"Contres : {', '.join(matchups['counter_picks'][:3])}\n"
                if 'good_against' in matchups:
                    formatted_data += f"Avantagé contre : {', '.join(matchups['good_against'][:3])}\n"
        
        return formatted_data

    def get_response(self, query: str) -> Optional[str]:
        """Obtient une réponse du modèle HuggingFace enrichie avec les données Riot"""
        try:
            # Enrichir le contexte avec les données Riot
            riot_context = self._enrich_context_with_riot_data(query)
            formatted_riot_data = self._format_riot_data_for_prompt(riot_context)
            
            # Construire le prompt complet avec les données Riot
            full_prompt = f"{self.system_prompt}\n{formatted_riot_data}\n\nQuestion: {query}\n\nRéponse:"
            
            # Paramètres de génération optimisés
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "do_sample": True,
                    "return_full_text": False,
                    "stop": ["Question:", "\n\n"]
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            # Traiter la réponse
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '').strip()
                
                # Nettoyer la réponse
                if "Réponse:" in generated_text:
                    generated_text = generated_text.split("Réponse:")[1].strip()
                
                return generated_text
            
            return None
            
        except Exception as e:
            print(f"Erreur lors de l'appel à HuggingFace: {str(e)}")
            return None 