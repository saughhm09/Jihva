import os
from typing import Dict, Any
from pyannote.audio import Pipeline # type: ignore

# Load pipeline. Requires HF_TOKEN in environment variables
# Before running this, ensure you have accepted the user conditions on huggingface pyannote pages
hf_token = os.environ.get("HF_TOKEN", None)
try:
    diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)
except Exception as e:
    # try older/newer versions which might use use_auth_token or simply token
    try:
        diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=hf_token)
    except Exception as e2:
        print(f"Failed to load speaker diarization from pyannote: {e} | {e2}")
        diarization_pipeline = None


def diarize_audio(audio_path, num_speakers=None):
    """
    Perform speaker diarization.
    Returns a list of segments: [{'speaker': 'SPEAKER_00', 'start': 0.0, 'end': 2.5}, ...]
    """
    if diarization_pipeline is None:
        print("Diarization skipped: pipeline not loaded (Check HF_TOKEN).")
        return []
        
    # Apply the pipeline to an audio file
    # We can pass num_speakers if provided by the user (2-5)
    try:
        diarization = diarization_pipeline(audio_path, num_speakers=num_speakers)
    except Exception as e:
        print(f"Diarization failed during processing: {e}")
        return []
    
    segments = []
    
    # process the result
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end
        })
        
    return segments


def format_time(seconds):
    """Convert seconds to MM:SS format"""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def merge_transcription_and_diarization(whisper_segments, pyannote_segments):
    """
    Merges word-level/segment-level timestamps from whisper with speaker chunks from pyannote.
    Outputs format: [Speaker 1 | 00:00-00:05]: Hello everyone
    """
    # Extremely simplified matching. A robust implementation would match word-by-word.
    # For speed and simplicity, we'll assign each whisper segment to the speaker 
    # who speaks the most during that segment.
    
    merged_output = []
    speaker_map: Dict[str, str] = {} # Maps SPEAKER_00 -> Speaker 1
    
    for w_seg in whisper_segments:
        w_start = w_seg["start"]
        w_end = w_seg["end"]
        w_mid = (w_start + w_end) / 2
        
        assigned_speaker = "Unknown"
        
        # Find which pyannote segment contains the midpoint of this whisper segment
        for p_seg in pyannote_segments:
            if p_seg["start"] <= w_mid <= p_seg["end"]:
                raw_speaker = str(p_seg["speaker"])
                if raw_speaker not in speaker_map:
                    speaker_map[raw_speaker] = f"Speaker {len(speaker_map) + 1}"
                assigned_speaker = speaker_map.get(raw_speaker, "Unknown")
                break
                
        merged_output.append({
            "speaker": assigned_speaker,
            "start": w_start,
            "end": w_end,
            "time_str": f"[{assigned_speaker} | {format_time(w_start)}–{format_time(w_end)}]",
            "text": w_seg["text"]
        })
        
    return merged_output
