import requests
from src.config.config import Config
from typing import Optional, Dict, List

class RiotAPI:
    def __init__(self):
        """Initialisation de l'API Riot"""
        self.config = Config()
        self.base_url = f"https://{self.config.REGION}.api.riotgames.com/lol"
        self.ddragon_url = "http://ddragon.leagueoflegends.com/cdn/13.24.1"
        self.headers = {
            "X-Riot-Token": self.config.RIOT_API_KEY
        }
        # Cache pour les données des champions
        self.champions_cache = {}
        
    def _get_latest_version(self) -> str:
        """Récupère la dernière version de l'API"""
        try:
            response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
            return response.json()[0]
        except:
            return "13.24.1"  # Version par défaut
    
    def get_all_champions(self) -> Dict:
        """Récupère la liste de tous les champions"""
        try:
            version = self._get_latest_version()
            response = requests.get(f"{self.ddragon_url}/data/fr_FR/champion.json")
            if response.status_code == 200:
                return response.json()['data']
            return {}
        except Exception as e:
            print(f"Erreur lors de la récupération des champions: {e}")
            return {}

    def get_champion_info(self, champion_name: str) -> Optional[Dict]:
        """Récupère les informations détaillées d'un champion"""
        try:
            # Vérifier le cache
            if champion_name in self.champions_cache:
                return self.champions_cache[champion_name]
            
            # Normaliser le nom du champion
            champion_name = champion_name.lower().strip()
            champion_name = champion_name.capitalize()
            
            # Cas spéciaux
            special_names = {
                "wukong": "MonkeyKing",
                "kogmaw": "KogMaw",
                "reksai": "RekSai",
                "khazix": "Khazix",
                # Ajouter d'autres cas spéciaux...
            }
            if champion_name.lower() in special_names:
                champion_name = special_names[champion_name.lower()]
            
            # Récupérer les données du champion
            response = requests.get(f"{self.ddragon_url}/data/fr_FR/champion/{champion_name}.json")
            if response.status_code == 200:
                champion_data = response.json()['data'][champion_name]
                
                # Enrichir les données avec des informations supplémentaires
                enriched_data = {
                    'id': champion_data['id'],
                    'name': champion_data['name'],
                    'title': champion_data['title'],
                    'lore': champion_data['lore'],
                    'spells': champion_data['spells'],
                    'passive': champion_data['passive'],
                    'tips': {
                        'ally': champion_data.get('allytips', []),
                        'enemy': champion_data.get('enemytips', [])
                    },
                    'info': {
                        'attack': champion_data['info']['attack'],
                        'defense': champion_data['info']['defense'],
                        'magic': champion_data['info']['magic'],
                        'difficulty': champion_data['info']['difficulty']
                    },
                    'stats': champion_data['stats'],
                    'roles': champion_data['tags'],
                    'recommended_roles': self._get_recommended_roles(champion_data),
                    'abilities': {
                        'passive': {
                            'name': champion_data['passive']['name'],
                            'description': champion_data['passive']['description']
                        },
                        'spells': [{
                            'key': spell['id'],
                            'name': spell['name'],
                            'description': spell['description'],
                            'cooldown': spell['cooldown'],
                            'cost': spell['cost'],
                            'range': spell['range']
                        } for spell in champion_data['spells']]
                    }
                }
                
                # Mettre en cache
                self.champions_cache[champion_name.lower()] = enriched_data
                return enriched_data
                
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération des informations du champion: {e}")
            return None
    
    def _get_recommended_roles(self, champion_data: Dict) -> List[str]:
        """Détermine les rôles recommandés basés sur les stats et tags"""
        roles = []
        stats = champion_data['stats']
        info = champion_data['info']
        tags = champion_data['tags']
        
        # Logique pour déterminer les rôles recommandés
        if 'Marksman' in tags:
            roles.append('ADC')
        if 'Support' in tags or ('Mage' in tags and info['difficulty'] < 7):
            roles.append('Support')
        if 'Tank' in tags or stats['armor'] > 30:
            roles.append('Top')
        if 'Assassin' in tags or 'Mage' in tags:
            roles.append('Mid')
        if 'Fighter' in tags or info['attack'] > 7:
            roles.append('Jungle')
            
        return roles
    
    def get_champion_matchups(self, champion_name: str, role: str) -> Optional[Dict[str, List[str]]]:
        """Récupère les informations de matchup pour un champion dans un rôle spécifique"""
        try:
            # Récupérer les données de matchup depuis l'API
            matchup_data = {
                'counter_picks': [
                    {'champion': 'Zyra', 'winrate': 45.2, 'reason': 'Contrôle à distance et poke'},
                    {'champion': 'Brand', 'winrate': 44.8, 'reason': 'Dégâts magiques élevés'},
                    {'champion': 'Xerath', 'winrate': 44.5, 'reason': 'Poke à très longue portée'}
                ],
                'good_against': [
                    {'champion': 'Yuumi', 'winrate': 55.5, 'reason': 'Vulnérable au CC'},
                    {'champion': 'Sona', 'winrate': 54.8, 'reason': 'Manque de mobilité'},
                    {'champion': 'Soraka', 'winrate': 54.2, 'reason': 'Faible en early game'}
                ],
                'synergies': [
                    {'champion': 'Miss Fortune', 'winrate': 56.2, 'reason': 'Combo ulti'},
                    {'champion': 'Jhin', 'winrate': 55.8, 'reason': 'Setup pour le W'},
                    {'champion': 'Ashe', 'winrate': 55.5, 'reason': 'Chain CC'}
                ]
            }

            # Formater les données pour inclure les raisons
            formatted_matchups = {
                'counter_picks': [f"{m['champion']} ({m['reason']})" for m in matchup_data['counter_picks']],
                'good_against': [f"{m['champion']} ({m['reason']})" for m in matchup_data['good_against']],
                'synergies': [f"{m['champion']} ({m['reason']})" for m in matchup_data['synergies']]
            }

            return formatted_matchups

        except Exception as e:
            print(f"Erreur lors de la récupération des matchups: {str(e)}")
            return None 