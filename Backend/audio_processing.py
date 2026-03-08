import os
import numpy as np # type: ignore
import librosa # type: ignore
import noisereduce as nr # type: ignore
import soundfile as sf # type: ignore
from pydub import AudioSegment # type: ignore


def normalize_audio(audio_data):
    """Normalize amplitude between -1 and 1."""
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        return audio_data / max_val
    return audio_data


def remove_noise(audio_data, sr=16000):
    """Spectral gating noise reduction."""
    reduced_noise = nr.reduce_noise(y=audio_data, sr=sr)
    return reduced_noise


def remove_silence(audio_data, sr=16000, aggressiveness=3):
    """Remove non-speech regions using librosa (WebRTCvad failed to build)."""
    # Use librosa to trim leading/trailing silence and split on internal silence
    intervals = librosa.effects.split(audio_data, top_db=20)
    
    voiced_frames = []
    for interval in intervals:
        voiced_frames.extend(audio_data[interval[0]:interval[1]])
        
    return np.array(voiced_frames)


def extract_features(audio_path):
    """Extract MFCC (13), Spectrogram, Chroma, Zero Crossing Rate."""
    y, sr = librosa.load(audio_path, sr=16000)
    
    # MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    # Spectrogram (Mel)
    mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
    mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)
    
    # Chroma
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    
    # Zero Crossing Rate
    zcr = librosa.feature.zero_crossing_rate(y)
    
    return {
        "mfcc": mfcc.tolist(),
        "spectrogram": mel_spectrogram_db.tolist(),
        "chroma": chroma.tolist(),
        "zcr": zcr.tolist()
    }


def process_audio_file(file_path, apply_noise_reduction=True, apply_silence_removal=False):
    """End-to-end preprocessing pipeline for an audio file."""
    y, sr = librosa.load(file_path, sr=16000)
    
    if apply_noise_reduction:
        y = remove_noise(y, sr)
        
    if apply_silence_removal:
        y = remove_silence(y, sr)
        
    y = normalize_audio(y)
    
    # Save the processed audio temporarily
    output_path = file_path.replace(".wav", "_processed.wav").replace(".mp3", "_processed.wav")
    sf.write(output_path, y, sr)
    
    return output_path
