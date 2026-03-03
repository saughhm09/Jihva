from transformers import AutoModelForSeq2SeqLM, AutoTokenizer # type: ignore
from typing import Any, Dict, List

summarizer: Any = None # type: ignore

class CustomSummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        try:
            import torch # type: ignore
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        except:
            self.device = "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        
    def __call__(self, text, max_length=150, min_length=50, do_sample=False):
        inputs = self.tokenizer(text, return_tensors="pt", max_length=1024, truncation=True).to(self.device)
        summary_ids = self.model.generate(
            inputs["input_ids"], 
            max_length=max_length, 
            min_length=min_length, 
            do_sample=do_sample
        )
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return [{"summary_text": summary}]

def _init_model():
    global summarizer
    if summarizer is None:
        try:
            summarizer = CustomSummarizer("facebook/bart-large-cnn")
        except Exception as e:
            print(f"Failed to load summarizer: {e}")
            summarizer = False

def chunk_text(text, max_chunk_size=1024):
    """Chunk long texts into smaller pieces based on roughly ~4 chars per token."""
    words = text.split()
    chunks: List[str] = []
    current_chunk: List[str] = []
    current_length: int = 0
    
    # Very roughly estimating tokens with word counts
    # 1024 tokens usually ~ 700 words. Let's chunk at 600 words to be safe.
    max_words: int = 600  
    
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks


def generate_summary(text, mode="Detailed"):
    """
    Generates summary based on mode:
    - Mode 1: Short (Executive)
    - Mode 2: Detailed
    - Mode 3: Bullet
    """
    _init_model()
    if not text.strip() or summarizer is None or summarizer is False:
        return ""
        
    s: Any = summarizer # type: ignore
    
    chunks: List[str] = chunk_text(text)
    chunk_summaries: List[str] = []
    
    for chunk in chunks:
        # Determine max_length based on chunk size and mode
        chunk_words = len(chunk.split())
        
        if mode == "Short":
            max_len = min(60, int(chunk_words * 0.5))
            min_len = min(20, int(max_len * 0.5))
        elif mode == "Detailed":
            max_len = min(150, int(chunk_words * 0.7))
            min_len = min(50, int(max_len * 0.5))
        else: # Bullet mode initial summarization
            max_len = min(100, int(chunk_words * 0.6))
            min_len = min(30, int(max_len * 0.5))
            
        # Ensure min_len isn't too large for the chunk
        if min_len >= max_len:
            min_len = max_len // 2
            
        if max_len < 10:
            chunk_summaries.append(chunk) # Too short to summarize
            continue
            
        res: Any = s(chunk, max_length=max_len, min_length=min_len, do_sample=False)
        chunk_summaries.append(res[0]['summary_text']) # type: ignore
        
    merged_summary = " ".join(chunk_summaries) # type: ignore
    
    # If there were many chunks, summarize the merged result again (Hierarchical)
    if len(chunks) > 1:
        words = len(merged_summary.split())
        max_l = min(150, int(words * 0.7))
        min_l = min(50, int(max_l * 0.5))
        if max_l >= 10:
            final_res: Any = s(merged_summary, max_length=max_l, min_length=min_l, do_sample=False)
            merged_summary = final_res[0]['summary_text'] # type: ignore
            
    # Post-processing based on mode
    if mode == "Bullet":
        # Convert sentences to bullet points heuristically
        sentences = [s.strip() for s in merged_summary.split(". ") if s.strip()]
        bullet_points = [f"• {s}." if not s.endswith(".") else f"• {s}" for s in sentences]
        return "\n".join(bullet_points)
        
    return merged_summary


def summarize_transcript(segments, text, mode="Detailed"):
    """
    Provides overall and per-speaker summaries.
    Segments: [{'speaker': 'Speaker 1', 'text': '...'}, ...]
    """
    overall_summary = generate_summary(text, mode=mode)
    
    # Per-speaker aggregation
    speaker_texts: Dict[str, List[str]] = {}
    for seg in segments:
        spk = seg.get("speaker", "Unknown")
        txt = seg.get("text", "")
        if spk not in speaker_texts:
            speaker_texts[spk] = []
        speaker_texts[spk].append(txt)
        
    speaker_summaries: Dict[str, str] = {}
    for spk, texts in speaker_texts.items():
        spk_full_text = " ".join(texts)
        if len(spk_full_text.split()) > 30: # Only summarize if they spoke enough
            speaker_summaries[spk] = generate_summary(spk_full_text, mode="Short")
        else:
            speaker_summaries[spk] = spk_full_text
            
    # Calculate compression ratio
    orig_len = len(text.split()) if isinstance(text, str) else 0
    comp_len = len(overall_summary.split())
    ratio = float(round(orig_len / comp_len, 2)) if comp_len > 0 else 0.0
    
    return {
        "overall": overall_summary,
        "per_speaker": speaker_summaries,
        "compression_ratio": ratio
    }
