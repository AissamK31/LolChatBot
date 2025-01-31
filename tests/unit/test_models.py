import pytest
from src.models.champion import Champion, ChampionStats

@pytest.fixture
def sample_champion_data():
    return {
        "id": "ahri",
        "name": "Ahri",
        "title": "The Nine-Tailed Fox",
        "lore": "Une vastaya dotée d'une connexion innée avec la magie du monde...",
        "tags": ["Mage", "Assassin"],
        "stats": {
            "hp": 526.0,
            "mp": 418.0,
            "armor": 21.0,
            "spellblock": 30.0,
            "attackdamage": 53.0,
            "attackspeed": 0.668
        },
        "passive": {"description": "Essence Theft"},
        "spells": [
            {"description": "Orb of Deception"},
            {"description": "Fox-Fire"},
            {"description": "Charm"},
            {"description": "Spirit Rush"}
        ],
        "info": {"difficulty": 7}
    }

def test_champion_creation(sample_champion_data):
    champion = Champion.from_api_response(sample_champion_data)
    assert champion.name == "Ahri"
    assert champion.title == "The Nine-Tailed Fox"
    assert isinstance(champion.stats, ChampionStats)

def test_champion_stats(sample_champion_data):
    champion = Champion.from_api_response(sample_champion_data)
    assert champion.stats.hp == 526.0
    assert champion.stats.mp == 418.0
    assert champion.stats.armor == 21.0

def test_invalid_champion_data():
    with pytest.raises(KeyError):
        Champion.from_api_response({"invalid": "data"})

def test_champion_str_representation(sample_champion_data):
    champion = Champion.from_api_response(sample_champion_data)
    description = champion.get_brief_description()
    assert champion.name in description
    assert champion.title in description

def test_champion_abilities(sample_champion_data):
    champion = Champion.from_api_response(sample_champion_data)
    assert champion.get_ability_description("Q") == "Orb of Deception"
    assert champion.get_ability_description("W") == "Fox-Fire"
    assert champion.get_ability_description("E") == "Charm"
    assert champion.get_ability_description("R") == "Spirit Rush" 