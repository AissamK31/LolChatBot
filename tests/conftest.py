import pytest
import sys
import os

# Ajout du chemin du projet aux chemins Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def config():
    """Fixture pour la configuration de test"""
    from src.config.config import Config
    return Config()

@pytest.fixture
def chatbot():
    """Fixture pour le chatbot"""
    from src.chatbot.chatbot import LolChatbot
    return LolChatbot() 