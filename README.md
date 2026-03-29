# Jihvā — Multi-Speaker Speech Intelligence Engine

> Sanskrit for "Tongue" — a Retro Steampunk NLP engine that listens, understands, and analyzes speech.

Jihvā processes live microphone recordings or uploaded audio files through a full NLP pipeline, visualized in a pixel-art steampunk UI.

---

## Features

- **Audio Preprocessing** — Noise reduction and silence removal via librosa
- **Transcription** — Faster Whisper (medium model, CPU/CUDA) with filler word removal
- **Speaker Diarization** — Pyannote 3.1 (requires HuggingFace token + model access)
- **Sentiment Analysis** — Per-speaker sentiment using DistilBERT (SST-2)
- **Keyword Extraction** — Weighted noun/entity extraction via spaCy
- **Accent Detection** — Simulated Indian English accent classifier (MFCC + Random Forest)
- **Summarization** — Multi-mode BART summarization (Detailed / Short / Bullet)

---

## Project Structure

```
Jihva/
├── Backend/
│   ├── main.py                 # FastAPI server + pipeline orchestration
│   ├── audio_processing.py     # Noise reduction, silence removal, feature extraction
│   ├── transcription.py        # Faster Whisper transcription
│   ├── diarization.py          # Pyannote speaker diarization (lazy-loaded)
│   ├── sentiment.py            # DistilBERT sentiment analysis
│   ├── keyword_extraction.py   # spaCy keyword extraction
│   ├── accent.py               # Mock accent classifier
│   ├── summarization.py        # BART summarization
│   ├── requirements.txt
│   └── .env                    # HF_TOKEN goes here (not committed to git)
└── Frontend/                   # React + Vite app
    ├── src/
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── components/
    │   ├── HeaderSection.jsx
    │   ├── ControlPanel.jsx
    │   ├── TranscriptTerminal.jsx
    │   ├── Analytics.jsx
    │   ├── KeywordAnalyzer.jsx
    │   └── SummaryChamber.jsx
    ├── index.html
    ├── vite.config.js
    └── package.json
```

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- **FFmpeg** installed and added to PATH (required for audio decoding)
  - Windows: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
  - Or via winget: `winget install ffmpeg`

---

### Backend Setup

```bash
cd Backend
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Download the spaCy language model:

```bash
python -m spacy download en_core_web_sm
```

Pre-download the Whisper model (do this once to avoid delays on first request):

```bash
python -c "from faster_whisper import WhisperModel; WhisperModel('medium', device='cpu', compute_type='int8')"
```

Configure your environment — edit `Backend/.env`:

```
HF_TOKEN=hf_your_token_here
```

> The HF_TOKEN is only needed for speaker diarization. The rest of the pipeline works without it.

Run the server:

```bash
python main.py
```

The API will be available at `http://localhost:8000`.

---

### Speaker Diarization Setup (Optional)

Diarization requires a HuggingFace account and manual access approval:

1. Create a token at [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) (read access)
2. Accept terms at [https://huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
3. Accept terms at [https://huggingface.co/pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
4. Paste your token into `Backend/.env`

Without a token, the app falls back to single-speaker mode (all segments labeled "Unknown").

---

### Frontend Setup

```bash
cd Frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173` and proxies API calls to the backend automatically.

---

## API Reference

### `POST /api/process-audio`

Accepts `multipart/form-data`:

| Field | Type | Default | Description |
|---|---|---|---|
| `file` | File | required | Audio file (WAV, MP3, WebM) |
| `num_speakers` | int | 2 | Expected number of speakers (2–5) |
| `remove_fillers` | bool | false | Strip filler words (um, uh, like...) |
| `noise_reduction` | bool | true | Apply spectral noise reduction |
| `silence_removal` | bool | false | Remove silent regions |
| `summary_mode` | string | Detailed | Detailed / Short / Bullet |

Returns JSON:

```json
{
  "status": "success",
  "segments": [
    {
      "speaker": "Speaker 1",
      "start": 0.0,
      "end": 3.2,
      "time_str": "[Speaker 1 | 00:00–00:03]",
      "text": "Hello hello hello hello."
    }
  ],
  "full_text": "Hello hello hello hello.",
  "language_info": { "language": "en", "confidence": 0.99 },
  "sentiment": {
    "Speaker 1": { "positive": 100.0, "neutral": 0.0, "negative": 0.0 }
  },
  "keywords": { "hello": 4 },
  "accent": {
    "prediction": "Neutral Indian",
    "confidences": { "North Indian": 30.0, "South Indian": 25.0, "Neutral Indian": 45.0 }
  },
  "summary": {
    "overall": "...",
    "per_speaker": { "Speaker 1": "..." },
    "compression_ratio": 1.5
  }
}
```

---

## Known Limitations

- Accent detection is a mock classifier (random forest on dummy data). A real implementation requires a labeled Indian English accent dataset.
- Whisper is forced to English (`language="en"`). Change this in `transcription.py` if you need multilingual support.
- Diarization requires gated HuggingFace model access and will be skipped without a valid token.
- The `PySoundFile` warning on Windows is harmless — librosa falls back to audioread automatically.
