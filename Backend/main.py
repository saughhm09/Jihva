import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
import shutil
import uuid

# Import custom modules
from audio_processing import process_audio_file, extract_features # type: ignore
from transcription import transcribe_audio # type: ignore
from diarization import diarize_audio, merge_transcription_and_diarization # type: ignore
from sentiment import analyze_sentiment # type: ignore
from keyword_extraction import extract_keywords # type: ignore
from accent import detect_accent # type: ignore
from summarization import summarize_transcript # type: ignore

app = FastAPI(title="Jihvā - Retro Steampunk Speech & NLP Engine")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure temp directory exists
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/api/process-audio")
async def api_process_audio(
    file: UploadFile = File(None),
    num_speakers: int = Form(int),
    remove_fillers: bool = Form(False),
    noise_reduction: bool = Form(True),
    silence_removal: bool = Form(False),
    summary_mode: str = Form("Detailed")
):
    if not file:
        raise HTTPException(status_code=400, detail="No audio file provided.")
        
    # Save uploaded file
    file_id = str(uuid.uuid4())
    temp_path = os.path.join(TEMP_DIR, f"{file_id}_{file.filename}")
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 1. Preprocessing
        processed_path = process_audio_file(
            temp_path, 
            apply_noise_reduction=noise_reduction, 
            apply_silence_removal=silence_removal
        )
        
        # 2. Extract Acoustic Features
        features = extract_features(processed_path)
        
        # 3. Transcription
        transcription_result = transcribe_audio(processed_path, remove_fillers=remove_fillers)
        whisper_segments = transcription_result["segments"]
        language_info = {
            "language": transcription_result["language"],
            "confidence": transcription_result["language_confidence"]
        }
        
        # 4. Diarization
        pyannote_segments = diarize_audio(processed_path, num_speakers=num_speakers if num_speakers > 1 else None)
        
        # 5. Merge
        merged_segments = merge_transcription_and_diarization(whisper_segments, pyannote_segments)
        # If pyannote fails or single speaker, fallback to purely whisper segments
        if not merged_segments and whisper_segments:
             merged_segments = [{
                 "speaker": "Speaker 1",
                 "start": s["start"], "end": s["end"], 
                 "time_str": f"[00:00-00:00]", # Placeholder time struct
                 "text": s["text"]
             } for s in whisper_segments]
             
        full_text = transcription_result["full_text"]
        
        # 6. Sentiment
        sentiments = analyze_sentiment(merged_segments)
        
        # 7. Keywords
        keywords = extract_keywords(full_text)
        
        # 8. Accent
        accent = detect_accent(processed_path)
        
        # 9. Summarization
        summary = summarize_transcript(merged_segments, full_text, mode=summary_mode)
        
        return JSONResponse(content={
            "status": "success",
            "segments": merged_segments,
            "full_text": full_text,
            "language_info": language_info,
            "sentiment": sentiments,
            "keywords": keywords,
            "accent": accent,
            "summary": summary,
            "features_summary": {
                "mfcc_shape": len(features["mfcc"]),
                "note": "Acoustic features extracted for UI visualization"
            }
        })
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Cleanup temp files
        if os.path.exists(temp_path):
            try: os.remove(temp_path)
            except: pass
        processed_file = temp_path.replace(".wav", "_processed.wav").replace(".mp3", "_processed.wav")
        if os.path.exists(processed_file):
            try: os.remove(processed_file)
            except: pass

# The frontend is now served separately via React

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
