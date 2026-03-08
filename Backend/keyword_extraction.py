import spacy # type: ignore
from collections import Counter
import math

# Load the small english core web model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


def extract_keywords(text, top_n=10):
    """
    Extracts top keywords using Nouns/Entities and frequency.
    For true TF-IDF, we would need a corpus. We simulate the logic by weighting Entities and Nouns.
    """
    doc = nlp(text)
    
    # Filter stopwords and punctuation
    valid_tokens = [token for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    
    keywords = []
    
    # 1. Named Entities get a high weight
    for ent in doc.ents:
        if ent.label_ not in ["CARDINAL", "ORDINAL", "DATE", "TIME"]: # Filter out numbers/dates usually not "keywords"
            keywords.extend([ent.text.lower()] * 3) # Weight factor of 3
            
    # 2. Add Nouns and Proper Nouns
    for token in valid_tokens:
        if token.pos_ in ["NOUN", "PROPN"]:
            keywords.append(token.lemma_.lower())
            
    # Count frequencies
    word_freq = Counter(keywords)
    
    # Return top N
    return dict(word_freq.most_common(top_n)) # type: ignore
