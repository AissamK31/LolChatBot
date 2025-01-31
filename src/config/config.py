import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        # APIs
        self.HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
        self.RIOT_API_KEY = os.getenv('RIOT_API_KEY')
        self.REGION = os.getenv('REGION', 'euw1')
        
        # URLs
        self.DDRAGON_URL = "http://ddragon.leagueoflegends.com/cdn/13.24.1"
        self.HUGGINGFACE_MODEL_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
        
        # Paramètres
        self.SIMILARITY_THRESHOLD = 0.3
        self.MAX_RESPONSE_LENGTH = 200 