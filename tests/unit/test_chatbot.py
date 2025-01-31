import pytest
from unittest.mock import Mock, patch
from src.chatbot.chatbot import LolChatbot

@pytest.fixture
def mock_chatbot():
    with patch('src.chatbot.chatbot.RiotAPI') as mock_riot, \
         patch('src.chatbot.chatbot.HuggingFaceAPI') as mock_hf:
        
        # Configuration du mock Riot API
        mock_riot_instance = mock_riot.return_value
        mock_riot_instance.get_champion_info.return_value = {
            "name": "Ahri",
            "title": "The Nine-Tailed Fox",
            "lore": "Test lore",
            "spells": [
                {"description": "Orb of Deception"},
                {"description": "Fox-Fire"},
                {"description": "Charm"},
                {"description": "Spirit Rush"}
            ]
        }
        
        # Configuration du mock HuggingFace API
        mock_hf_instance = mock_hf.return_value
        mock_hf_instance.get_response.return_value = "Je ne peux pas répondre à cette question."
        
        chatbot = LolChatbot()
        yield chatbot

def test_chatbot_initialization():
    chatbot = LolChatbot()
    assert chatbot is not None
    assert hasattr(chatbot, 'knowledge_base')

def test_chatbot_general_knowledge():
    chatbot = LolChatbot()
    response = chatbot.get_response("Qu'est-ce que League of Legends?")
    assert "League of Legends" in response
    assert "MOBA" in response

@pytest.mark.parametrize("input_text", [
    "",
    "123",
    "a",
    "test"
])
def test_chatbot_invalid_inputs(input_text):
    chatbot = LolChatbot()
    response = chatbot.get_response(input_text)
    assert "je ne comprends pas" in response.lower() or "désolé" in response.lower()

def test_champion_query(mock_chatbot):
    response = mock_chatbot.get_response("Qui est Ahri?")
    assert "Ahri" in response
    assert "Nine-Tailed Fox" in response
    assert "Test lore" in response

def test_ability_query(mock_chatbot):
    response = mock_chatbot.get_response("Quel est le Q d'Ahri?")
    assert "Orb of Deception" in response

def test_invalid_query(mock_chatbot):
    response = mock_chatbot.get_response("xyz123")
    assert "ne peux pas répondre" in response.lower()

def test_none_input():
    chatbot = LolChatbot()
    with pytest.raises(AttributeError):
        chatbot.get_response(None) 