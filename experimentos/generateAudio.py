import numpy as np
import sounddevice as sd
import time

# Frequências fundamentais para as notas da oitava 4
frequencies = {
    "do": 261.63,
    "re": 293.66,
    "mi": 329.63,
    "fa": 349.23,
    "sol": 392.00,
    "la": 440.00,
    "si": 493.88,
}

freqAdjustFactor = 1

def generate_note(note, octave, duration=1.0, sample_rate=44100):
    freq = frequencies[note.lower()] * (2 ** (octave - 4))/freqAdjustFactor
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio_data = 0.5 * np.sin(2 * np.pi * freq * t)
    return audio_data

def play_notes(notes, octaves, duration=500.0, sample_rate=44100):
    audio_data = np.zeros(int(sample_rate * duration))

    for note in notes:
        for octave in octaves:
            audio_data += generate_note(note, octave, duration, sample_rate)

    # Normaliza o áudio para evitar clipping
    audio_data = audio_data / (len(notes) * len(octaves))

    sd.play(audio_data, samplerate=sample_rate)
    sd.wait()

# Todas as 7 notas e 8 oitavas
all_notes = ["do", "re", "mi", "fa", "sol", "la", "si"]
all_octaves = [1, 2, 3, 4, 5, 6, 7, 8]

# Toca todas as notas e oitavas simultaneamente
play_notes(all_notes, all_octaves)
