from transformers import pipeline # type: ignore

from typing import Any, Dict

sentiment_pipeline: Any = None

def _init_model():
    global sentiment_pipeline
    if sentiment_pipeline is None:
        try:
            sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=-1)
        except Exception as e:
            print(f"Failed to load sentiment pipeline: {e}")
            sentiment_pipeline = False

def analyze_sentiment(text_segments):
    """
    Analyze sentiment per speaker/sentence.
    Returns the distribution of emotions.
    text_segments should be a list of dicts with 'speaker' and 'text'.
    """
    _init_model()
    if sentiment_pipeline is None or sentiment_pipeline is False or not text_segments:
        return {}
        
    sp: Any = sentiment_pipeline
        
    speaker_sentiments: Dict[str, Dict[str, int]] = {}
    
    for segment in text_segments:
        speaker = segment.get("speaker", "Unknown")
        text = segment.get("text", "").strip()
        
        if not text:
            continue
            
        # Due to 512 token limit on distilbert, we might need to truncate
        # but typical whisper segments are short enough
        if len(text) > 2000:
            text = text[:2000]
            
        try:
            result = sp(text)[0] # type: ignore
            label = result['label'] # POSITIVE or NEGATIVE
            score = result['score']
        except Exception:
            continue
            
        if speaker not in speaker_sentiments:
            speaker_sentiments[speaker] = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0, "total": 0}
            
        # SST-2 is binary, so we simulate Neutral if confidence is very low (~0.5)
        if 0.45 <= score <= 0.55:
            speaker_sentiments[speaker]["NEUTRAL"] += 1
        else:
            speaker_sentiments[speaker][label] += 1
            
        speaker_sentiments[speaker]["total"] += 1
        
    # Convert counts to percentages
    final_stats: Dict[str, Dict[str, float]] = {}
    for spk, stats in speaker_sentiments.items():
        total = stats["total"]
        if total > 0:
            final_stats[spk] = {
                "positive": float(round((stats["POSITIVE"] / total) * 100, 1)), # type: ignore
                "neutral": float(round((stats["NEUTRAL"] / total) * 100, 1)), # type: ignore
                "negative": float(round((stats["NEGATIVE"] / total) * 100, 1)) # type: ignore
            }
            
    return final_stats
