from faster_whisper import WhisperModel # type: ignore
import re
from deepmultilingualpunctuation import PunctuationModel # type: ignore

from typing import Any, List, Dict

# Defer initialization until first run
whisper_model: Any = None
punct_model: Any = None

FILLER_WORDS: List[str] = [r'\bum\b', r'\buh\b', r'\blike\b', r'\byou know\b', r'\bbasically\b', r'\bactually\b', r'\bkind of\b', r'\bsort of\b']


def _init_models():
    global whisper_model, punct_model
    if whisper_model is None:
        MODEL_SIZE = "medium"
        try:
            import torch # type: ignore
            if torch.cuda.is_available():
                whisper_model = WhisperModel(MODEL_SIZE, device="cuda", compute_type="float16")
                print("Faster Whisper loaded on CUDA")
            else:
                whisper_model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
                print("Faster Whisper loaded on CPU (CUDA unavailable via PyTorch)")
        except Exception as e:
            print(f"CUDA failed or not available, falling back to CPU. Error: {e}")
            whisper_model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

    if punct_model is None:
        try:
            punct_model = PunctuationModel()
        except Exception as e:
            print(f"Punctuation model failed to load. Will skip punctuation restoration if so. Error: {e}")
            punct_model = False # Set to false to avoid retrying


def transcribe_audio(audio_path, remove_fillers=False):
    """Transcribes audio, returning timestamps and word-level details."""
    _init_models()
    assert whisper_model is not None

    segments, info = whisper_model.transcribe(audio_path, word_timestamps=True)
    
    language = info.language
    overall_confidence = info.language_probability
    
    transcribed_segments: List[Dict[str, Any]] = []
    full_text = ""
    
    for segment in segments:
        text = segment.text
        if remove_fillers:
            for filler in FILLER_WORDS:
                text = re.sub(filler, '', text, flags=re.IGNORECASE)
            # clean up multiple spaces created by removal
            text = re.sub(r'\s+', ' ', text).strip()
            
        transcribed_segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": text
        })
        full_text += text + " "
        
    # Apply punctuation restoration if the model loaded
    if punct_model and full_text.strip():
        try:
            full_text = punct_model.restore_punctuation(full_text)
            # You could also try mapping punct back to segments but that can get tricky.
        except Exception as e:
            print(f"Warning: Punctuation restoration failed: {e}")
            
    return {
        "language": language,
        "language_confidence": overall_confidence,
        "segments": transcribed_segments,
        "full_text": full_text.strip()
    }
