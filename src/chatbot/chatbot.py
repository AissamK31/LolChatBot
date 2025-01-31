from src.config.config import Config
from src.api.riot_api import RiotAPI
from src.api.huggingface_api import HuggingFaceAPI
from src.utils.text_processing import initialize_nltk, find_best_match

class LolChatbot:
    def __init__(self):
        """Initialisation du chatbot"""
        self.config = Config()
        self.riot_api = RiotAPI()
        self.huggingface_api = HuggingFaceAPI()
        initialize_nltk()
        
        # Base de connaissances pour les questions générales
        self.knowledge_base = {
            "general": {
                "qu'est-ce que league of legends": "League of Legends est un jeu MOBA 5v5 développé par Riot Games.",
                "comment jouer": "Pour jouer, vous devez choisir un champion et rejoindre une équipe de 5 joueurs.",
                "quel est le but du jeu": "Le but est de détruire le Nexus ennemi en progressant à travers les tourelles."
            }
        }
    
    def get_response(self, query: str) -> str:
        """Génère une réponse à la question de l'utilisateur"""
        query = query.lower().strip()
        
        # Vérifier d'abord dans la base de connaissances
        for category, qa_pairs in self.knowledge_base.items():
            best_match, score = find_best_match(query, list(qa_pairs.keys()))
            if best_match and score > self.config.SIMILARITY_THRESHOLD:
                return qa_pairs[best_match]
        
        # Vérifier si c'est une question sur un champion
        if "qui est" in query or "quel champion" in query:
            champion_name = query.replace("qui est", "").replace("quel champion est", "").strip("? ")
            champion_info = self.riot_api.get_champion_info(champion_name)
            if champion_info:
                return f"{champion_info['name']} est {champion_info['title']}. {champion_info['lore'][:200]}..."
            return f"Désolé, je n'ai pas trouvé d'informations sur {champion_name}."
        
        # Vérifier si c'est une question sur une capacité
        if "capacité" in query or "spell" in query or "q" in query or "w" in query or "e" in query or "r" in query:
            # Extraire le nom du champion de la question
            words = query.split()
            champion_name = None
            for word in words:
                if "d'" in word:
                    champion_name = word.split("d'")[1]
                    break
            
            if champion_name:
                champion_info = self.riot_api.get_champion_info(champion_name)
                if champion_info:
                    ability_map = {
                        'q': 0, 'w': 1, 'e': 2, 'r': 3,
                        'spell1': 0, 'spell2': 1, 'spell3': 2, 'spell4': 3
                    }
                    for key, idx in ability_map.items():
                        if key in query:
                            return champion_info['spells'][idx]['description']
            return "Désolé, je n'ai pas compris de quel champion ou quelle capacité vous parlez."
        
        # Si la requête est invalide ou non reconnue
        if len(query.strip()) < 5 or query.strip().isdigit():
            return "Je suis désolé, je ne comprends pas votre question. Pourriez-vous la reformuler?"
        
        # En dernier recours, utiliser l'API HuggingFace
        try:
            response = self.huggingface_api.get_response(query)
            if response:
                return response
        except Exception as e:
            pass
        
        return "Désolé, je ne peux pas répondre à cette question pour le moment. Essayez de me poser une question différente." 