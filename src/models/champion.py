from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ChampionStats:
    hp: float
    mp: float
    armor: float
    spellblock: float
    attackdamage: float
    attackspeed: float

@dataclass
class Champion:
    id: str
    name: str
    title: str
    lore: str
    tags: List[str]
    stats: ChampionStats
    abilities: Dict[str, str]
    difficulty: int
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'Champion':
        """Crée une instance de Champion à partir des données de l'API"""
        return cls(
            id=data['id'],
            name=data['name'],
            title=data['title'],
            lore=data['lore'],
            tags=data['tags'],
            stats=ChampionStats(**data['stats']),
            abilities={
                'passive': data['passive']['description'],
                'Q': data['spells'][0]['description'],
                'W': data['spells'][1]['description'],
                'E': data['spells'][2]['description'],
                'R': data['spells'][3]['description']
            },
            difficulty=data['info']['difficulty']
        )
    
    def get_brief_description(self) -> str:
        """Retourne une description courte du champion"""
        return f"{self.name}, {self.title}. {self.lore[:200]}..."
    
    def get_ability_description(self, ability: str) -> Optional[str]:
        """Retourne la description d'une capacité spécifique"""
        return self.abilities.get(ability.upper()) 