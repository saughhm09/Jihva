import os
import warnings
from typing import Dict, Any, Optional

# Suppress the Pyannote torchcodec warnings about FFmpeg
warnings.filterwarnings("ignore", category=UserWarning, message=".*torchcodec is not installed correctly.*")

hf_token = os.environ.get("HF_TOKEN")

if not hf_token:
    print("HF_TOKEN not found in environment. Speaker diarization will be skipped.")

# Lazy-loaded pipeline — initialized on first use, not at import time
diarization_pipeline: Optional[Any] = None
_pipeline_load_attempted = False


def _init_pipeline():
    global diarization_pipeline, _pipeline_load_attempted
    if _pipeline_load_attempted:
        return
    _pipeline_load_attempted = True

    if not hf_token:
        return

    from pyannote.audio import Pipeline  # type: ignore
    try:
        diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1", use_auth_token=hf_token
        )
    except Exception:
        try:
            diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1", token=hf_token
            )
        except Exception as e2:
            print(f"Failed to load speaker diarization from pyannote. Check your HF_TOKEN. Error: {e2}")
            diarization_pipeline = None


def diarize_audio(audio_path, num_speakers=None):
    """
    Perform speaker diarization.
    Returns a list of segments: [{'speaker': 'SPEAKER_00', 'start': 0.0, 'end': 2.5}, ...]
    """
    _init_pipeline()

    if diarization_pipeline is None:
        print("Diarization skipped: pipeline not loaded (Check HF_TOKEN).")
        return []

    try:
        diarization = diarization_pipeline(audio_path, num_speakers=num_speakers)
    except Exception as e:
        print(f"Diarization failed during processing: {e}")
        return []

    segments = []
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
    Merges segment-level timestamps from whisper with speaker chunks from pyannote.
    Outputs format: [Speaker 1 | 00:00-00:05]: Hello everyone
    """
    merged_output = []
    speaker_map: Dict[str, str] = {}  # Maps SPEAKER_00 -> Speaker 1

    for w_seg in whisper_segments:
        w_start = w_seg["start"]
        w_end = w_seg["end"]
        w_mid = (w_start + w_end) / 2

        assigned_speaker = "Unknown"

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
