import requests
from src.config.config import Config

class HuggingFaceAPI:
    def __init__(self):
        """Initialisation de l'API HuggingFace"""
        self.config = Config()
        self.api_url = self.config.HUGGINGFACE_MODEL_URL
        self.headers = {
            "Authorization": f"Bearer {self.config.HUGGINGFACE_API_KEY}"
        }
    
    def get_response(self, query: str) -> str:
        """Obtient une réponse du modèle pour une question donnée"""
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": query}
            )
            
            if response.status_code == 200:
                return response.json()[0]['generated_text']
            else:
                print(f"Erreur API HuggingFace: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Erreur HuggingFace API: {e}")
            return None 