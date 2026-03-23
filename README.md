# Jihvā - Multi-Speaker Speech Recognition & NLP Intelligence Engine

Jihvā (Sanskrit for "Tongue") is a Retro Steampunk Pixel-Art Speech & NLP Intelligence Engine. It processes live audio or uploaded files, performing the following pipeline:
1. Preprocessing (Noise reduction, Silence removal)
2. Transcription (Faster Whisper)
3. Speaker Diarization (Pyannote)
4. Sentiment Analysis (Transformers)
5. Keyword Extraction (spaCy)
6. Accent Detection (Simulated via MFCC/Random Forest)
7. Multi-Mode Summarization (BART)

## Architecture
The application is structured into two main components:
- **Backend**: A FastAPI server handling the complex audio and NLP processing pipelines.
- **Frontend**: A React SPA built with Vite containing the Steampunk retro-style visualization layer.

## Setup Instructions

### 1. Backend Setup
Navigate into the `Backend` directory:
```bash
cd Backend
```

Install System Dependencies:
Ensure you have **FFmpeg** installed on your system and added to your PATH, as it is required for audio extraction.

Create a Virtual Environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

Install Python Dependencies:
```bash
pip install fastapi uvicorn python-multipart pydub faster-whisper deepmultilingualpunctuation transformers torch pyannote.audio spacy numpy librosa noisereduce soundfile scikit-learn requests
```

Download spaCy Language Model:
```bash
python -m spacy download en_core_web_sm
```

Run the Backend Server:
```bash
python main.py
```
*The API will start running on `http://localhost:8000`*

### 2. Frontend Setup
Navigate into the frontend directory:
```bash
cd Frontend/Frontend
```

Install Node Modules:
```bash
npm install
```

Run the Developer Server:
```bash
npm run dev
```
*The app will launch on your local network, communicating locally to the Python API using HTTP POST.*

## API Specification
The backend provides a single comprehensive endpoint for processing audio:

`POST /api/process-audio`

Accepts `multipart/form-data`:
- `file`: The audio file (WAV/MP3)
- `num_speakers`: (int) Target number of speakers.
- `remove_fillers`: (bool) 
- `noise_reduction`: (bool)
- `silence_removal`: (bool)
- `summary_mode`: (str) Detailed, Short, or Bullet.

Returns a comprehensive JSON payload containing transcription segments mapping to time arrays, per-speaker sentiment analysis, calculated keywords, regional accent metadata, and full text summarizations.