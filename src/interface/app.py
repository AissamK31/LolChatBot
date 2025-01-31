import os
import sys

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import streamlit as st
from streamlit_chat import message
from src.chatbot.chatbot import LolChatbot

# Configuration de la page
st.set_page_config(
    page_title="LoL Chatbot",
    page_icon="🎮",
    layout="centered"
)

def initialize_session_state():
    """Initialise les variables de session si elles n'existent pas"""
    try:
        if "chatbot" not in st.session_state:
            st.session_state.chatbot = LolChatbot()
            st.success("Chatbot initialisé avec succès!")
        if "messages" not in st.session_state:
            st.session_state.messages = []
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation : {str(e)}")

def main():
    try:
        initialize_session_state()
        
        st.title("🎮 League of Legends Chatbot")
        st.markdown("""
        Je suis un chatbot spécialisé dans League of Legends. Je peux vous aider avec :
        - Des informations sur les champions
        - Des détails sur leurs capacités
        - Des questions générales sur le jeu
        """)
        
        # Zone de chat
        if st.session_state.messages:
            for i, (role, content) in enumerate(st.session_state.messages):
                message(content, is_user=(role == "user"), key=f"{i}_{role}")
        
        # Zone de saisie
        user_input = st.chat_input("Posez votre question ici...")
        
        if user_input:
            # Ajouter le message de l'utilisateur
            st.session_state.messages.append(("user", user_input))
            
            # Obtenir la réponse du chatbot
            response = st.session_state.chatbot.get_response(user_input)
            
            # Ajouter la réponse du chatbot
            st.session_state.messages.append(("assistant", response))
            
            # Recharger la page pour afficher les nouveaux messages
            st.rerun()

        # Bouton pour effacer l'historique
        if st.button("Effacer l'historique"):
            st.session_state.messages = []
            st.rerun()
            
    except Exception as e:
        st.error(f"Une erreur s'est produite : {str(e)}")

if __name__ == "__main__":
    main() 