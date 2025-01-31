import nltk

def download_nltk_resources():
    resources = [
        'punkt',
        'stopwords',
        'averaged_perceptron_tagger'
    ]
    
    for resource in resources:
        try:
            nltk.download(resource)
            print(f"Successfully downloaded {resource}")
        except Exception as e:
            print(f"Error downloading {resource}: {e}")

if __name__ == "__main__":
    download_nltk_resources() 