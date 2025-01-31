import sys
print(f"Python version: {sys.version}")

# Test des dépendances de base
try:
    import requests
    import dotenv
    import numpy as np
    print("\n✅ Dépendances de base OK")
except ImportError as e:
    print(f"\n❌ Erreur dans les dépendances de base: {str(e)}")

# Test Machine Learning
try:
    import sklearn
    print(f"✅ scikit-learn version {sklearn.__version__} OK")
except ImportError as e:
    print(f"❌ Erreur avec scikit-learn: {str(e)}")

# Test NLP
try:
    import nltk
    import transformers
    print(f"✅ NLTK version {nltk.__version__} OK")
    print(f"✅ Transformers version {transformers.__version__} OK")
except ImportError as e:
    print(f"❌ Erreur avec les dépendances NLP: {str(e)}")

# Test Deep Learning
try:
    import torch
    print(f"✅ PyTorch version {torch.__version__} OK")
    print(f"CUDA disponible: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"❌ Erreur avec PyTorch: {str(e)}")

# Test autres dépendances
try:
    import tqdm
    import scipy
    print(f"✅ tqdm version {tqdm.__version__} OK")
    print(f"✅ scipy version {scipy.__version__} OK")
except ImportError as e:
    print(f"❌ Erreur avec les autres dépendances: {str(e)}")

print("\nTest terminé!") 