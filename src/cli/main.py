"""
Interface en ligne de commande pour le chatbot League of Legends.
"""

from src.chatbot.chatbot import LolChatbot

def main():
    print("Initialisation du chatbot...")
    try:
        chatbot = LolChatbot()
        print("\nBienvenue! Je suis votre assistant League of Legends avancé!")
        print("Je peux répondre à vos questions sur les champions et sur le jeu en général.")
        print("\nExemples de questions:")
        print("- Qui est Ahri?")
        print("- Explique-moi le rôle d'un support")
        print("- Comment fonctionne le système de classement?")
        print("\nTapez 'quit' pour quitter")
        
        while True:
            try:
                user_input = input("\nVous: ")
                if user_input.lower() == 'quit':
                    break
                    
                response = chatbot.get_response(user_input)
                print(f"Bot: {response}")
                
            except KeyboardInterrupt:
                print("\nAu revoir!")
                break
            except Exception as e:
                print(f"Une erreur est survenue: {str(e)}")
                print("N'hésitez pas à réessayer avec une autre question.")
                
    except Exception as e:
        print(f"Erreur lors de l'initialisation du chatbot: {str(e)}")
        print("Vérifiez vos clés API dans le fichier .env")

if __name__ == "__main__":
    main() 