import numpy as np
import sounddevice as sd
import time

def generate_white_noise(duration=1.0, sample_rate=44100):
    # Gera um ruído branco usando uma distribuição uniforme
    audio_data = np.random.uniform(-1, 1, int(sample_rate * duration))
    return audio_data

def play_white_noise(duration=60.0, sample_rate=44100):
    # Gera e toca o ruído branco
    audio_data = generate_white_noise(duration, sample_rate)
    sd.play(audio_data, samplerate=sample_rate)
    sd.wait()

# Toca ruído branco por 60 segundos
play_white_noise(duration=180.0)
