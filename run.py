import os
import sys

# Ajouter le répertoire du projet au PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Importer et lancer l'application Streamlit
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    # Définir les variables d'environnement
    os.environ["PYTHONPATH"] = project_root
    
    # Lancer l'application
    sys.argv = ["streamlit", "run", "src/interface/app.py", 
                "--server.port=8501",
                "--server.address=0.0.0.0",
                "--browser.serverAddress=localhost",
                "--server.headless=true",
                "--server.enableCORS=true",
                "--server.enableXsrfProtection=false"]
    
    sys.exit(stcli.main()) 