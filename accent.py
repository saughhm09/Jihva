"""
Backend module for detecting speaker accent (North/South/Neutral Indian) from audio.
Currently uses a simulated classifier.
"""

import numpy as np # type: ignore
import librosa # type: ignore
from sklearn.ensemble import RandomForestClassifier # type: ignore

# NOTE: This is a placeholder model. 
# A true North/South/Neutral Indian English accent classifier requires a labeled dataset.
# Since we lack one, this simulates the ML classification pipeline using MFCCs.

class MockAccentClassifier:
    """Mock classifier to simulate accent detection."""
    def __init__(self):
        """Initializes the mock RandomForest with dummy data."""
        # We would normally train a RandomForestClassifier here using MFCC features
        self.clf = RandomForestClassifier(n_estimators=10, random_state=42)
        # Dummy "training" on random data just to initialize the model
        dummy_X = np.random.rand(10, 13) # 10 samples, 13 MFCCs
        dummy_y = np.random.choice(["North Indian", "South Indian", "Neutral Indian"], 10)
        self.clf.fit(dummy_X, dummy_y)

    def predict(self, _mfcc_features):
        """
        Takes MFCC features and predicts accent confidences.
        Because our model is random dummy data, the prediction will be effectively arbitrary.
        In production, replace `dummy_X` with real features from `librosa.feature.mfcc()`.
        """
        # A real prediction returns probabilities
        # mfcc_means = np.mean(_mfcc_features, axis=1).reshape(1, -1) # (1, 13) shape
        # probs = self.clf.predict_proba(mfcc_means)[0]
        
        # Simulated Output
        probs = np.random.dirichlet(np.ones(3), size=1)[0] # type: ignore
        
        classes = ["North Indian", "South Indian", "Neutral Indian"]
        confidences = {
            classes[0]: float(round(probs[0] * 100, 1)),
            classes[1]: float(round(probs[1] * 100, 1)),
            classes[2]: float(round(probs[2] * 100, 1))
        }
        
        # Highest confidence is the predicted label
        prediction = max(confidences, key=lambda k: confidences[k])
        
        return {
            "prediction": prediction,
            "confidences": confidences
        }

# Singleton instance
ACCENT_MODEL = MockAccentClassifier()

def detect_accent(audio_path):
    """
    Extracts features and predicts Indian English accent from an audio file.
    """
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        # Predict using mock classifier
        return ACCENT_MODEL.predict(mfcc)
    except Exception as e:
        print(f"Error detecting accent: {e}")
        return {
            "prediction": "Unknown",
            "confidences": {"North Indian": 0.0, "South Indian": 0.0, "Neutral Indian": 0.0}
        }
