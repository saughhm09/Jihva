# Jihvā - Multi-Speaker Speech Recognition & NLP Intelligence Engine

Jihvā (Sanskrit for "Tongue") is a Retro Steampunk Pixel-Art Speech & NLP Intelligence Engine. It processes live audio or uploaded files, performing the following pipeline:
1. Preprocessing (Noise reduction, Silence removal)
2. Transcription (Faster Whisper)
3. Speaker Diarization (Pyannote)
4. Sentiment Analysis (Transformers)
5. Keyword Extraction (spaCy)
6. Accent Detection (Simulated via MFCC/Random Forest)
7. Multi-Mode Summarization (BART)

## Prerequisites & Installation

1. **Python 3.10+** is recommended.
2. Install FFmpeg on your system (Required for Audio Processing).
3. Clone/Download the repository.
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Install SpaCy English model (usually handled automatically, but if it fails):
   ```bash
   python -m spacy download en_core_web_sm
   ```

## HuggingFace Token Setup

Speaker diarization requires the `pyannote/speaker-diarization-3.1` model, which is gated. 
1. Go to [HuggingFace pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) and accept the user conditions.
2. Generate an Access Token in your HF Account Settings.
3. Set it as an environment variable before running the server:
   - Windows (PowerShell): `$env:HF_TOKEN="your_token_here"`
   - Windows (CMD): `set HF_TOKEN=your_token_here`
   - Linux/Mac: `export HF_TOKEN="your_token_here"`

## Model Downloads
- **Faster-Whisper**: The `medium` model will download automatically the first time you run a transcription.
- **Transformers (Sentiment & BART)**: `distilbert-base-uncased-finetuned-sst-2-english` and `facebook/bart-large-cnn` will download automatically on first run.
- **Deep Multilingual Punctuation**: Will download automatically.

*(Note: First run will be slower as models download to your local cache. Ensure you have ~6GB of free space).*

## How to Run

1. Start the FastAPI backend server from the project root:
   ```bash
   uvicorn backend.main:app --reload
   ```
2. The UI is mounted as static files in FastAPI. Simply open your browser and go to:
   ```
   http://localhost:8000
   ```
3. Use the interface to Record live audio or Upload a `.wav`/`.mp3`.

## Feature Explanations

- **Summarization**: Uses BART to chunk long transcripts and summarize them. Supports "Short" (Executive overview), "Detailed" (Lengthy), and "Bullet" modes. It summarizes the overall text, and then provides mini-summaries for what each individual speaker contributed.
- **Evaluation Metrics Space**: The UI calculates and displays a "Compression Ratio" metric in the Summary output panel, illustrating how condensed the final summary is compared to the original text length.
