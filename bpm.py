import librosa


def get_bpm(audio_path):
    """
    Calculate BPM of an audio file using librosa
    """
    # Load audio file with a lower sample rate
    y, sr = librosa.load(audio_path, sr=11025)

    # Calculate tempo using librosa's optimized beat tracker
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    # Extract scalar value from tempo array and convert to float
    return round(float(tempo.item()))
