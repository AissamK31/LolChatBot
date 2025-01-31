import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def initialize_nltk():
    """Initialise les ressources NLTK nécessaires"""
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("Téléchargement des ressources NLTK...")
        nltk.download('punkt')
        nltk.download('stopwords')
        print("Ressources NLTK téléchargées avec succès!")

def preprocess_text(text: str) -> str:
    """Prétraite le texte pour la comparaison"""
    # S'assurer que les ressources sont disponibles
    initialize_nltk()
    
    # Tokenisation et mise en minuscules
    tokens = word_tokenize(text.lower())
    
    # Suppression des stopwords
    stop_words = set(stopwords.words('french'))
    tokens = [token for token in tokens if token not in stop_words]
    
    return ' '.join(tokens)

def calculate_similarity(text1, text2):
    """Calcule la similarité cosinus entre deux textes"""
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except:
        return 0.0

def find_best_match(query: str, candidates: list) -> tuple:
    """Trouve la meilleure correspondance pour une requête donnée"""
    if not query or not candidates:
        return None, 0.0
    
    # Prétraitement
    processed_query = preprocess_text(query)
    processed_candidates = [preprocess_text(c) for c in candidates]
    
    # Vectorisation TF-IDF
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([processed_query] + processed_candidates)
    except ValueError:
        return None, 0.0
    
    # Calcul des similarités
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
    
    # Trouver le meilleur match
    if len(similarities) > 0:
        best_idx = np.argmax(similarities)
        return candidates[best_idx], similarities[best_idx]
    
    return None, 0.0 