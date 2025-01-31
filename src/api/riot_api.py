import requests
from src.config.config import Config

class RiotAPI:
    def __init__(self):
        """Initialisation de l'API Riot"""
        self.config = Config()
        self.base_url = f"https://{self.config.REGION}.api.riotgames.com/lol"
        self.ddragon_url = "http://ddragon.leagueoflegends.com/cdn/13.24.1"
        self.headers = {
            "X-Riot-Token": self.config.RIOT_API_KEY
        }
    
    def get_champion_info(self, champion_name: str) -> dict:
        """Récupère les informations d'un champion"""
        try:
            # Normaliser le nom du champion
            champion_name = champion_name.lower().strip()
            
            # Récupérer les données depuis Data Dragon
            response = requests.get(f"{self.ddragon_url}/data/fr_FR/champion/{champion_name}.json")
            if response.status_code == 200:
                data = response.json()
                champion_data = data['data'][champion_name]
                return champion_data
            
            return None
        except Exception as e:
            print(f"Erreur Riot API: {e}")
            return None 