import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

# Frequências fundamentais para as notas da oitava 4
frequencies = {
    "do": 261.63,
    "re": 293.66,
    "mi": 329.63,
    "fa": 349.23,
    "sol": 392.00,
    "la": 440.00,
    "si": 493.88,
    "23hz": 23/0.07,
    "24hz": 24/0.07,
    "25hz": 25/0.07,
}

def generate_note(note, octave, duration=1.0, sample_rate=44100, adjust_factor=0.07):
    freq = frequencies[note.lower()] * (2 ** (octave - 4)) * adjust_factor
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio_data = np.sin(2 * np.pi * freq * t)
    return audio_data

def save_wav(filename, data, sample_rate):
    # Ajuste a amplitude antes de converter para int16
    data = np.int16(data / np.max(np.abs(data)) * 32767)
    write(filename, sample_rate, data)

def play_notes(notes, octaves, duration=180.0, sample_rate=44100):
    audio_data = np.zeros(int(sample_rate * duration))

    for note in notes:
        for octave in octaves:
            audio_data += generate_note(note, octave, duration, sample_rate)

    # Salva o arquivo WAV
    save_wav("Audio2min_23a25hz.wav", audio_data, sample_rate)

    # Toca o áudio
    sd.play(audio_data, samplerate=sample_rate)
    sd.wait()

# Todas as 7 notas e 8 oitavas
all_notes = ["do", "re", "mi", "fa", "sol", "la", "si"]
all_octaves = [3, 4, 5]
# all_notes = ["24hz"]
# all_octaves = [1,2,3,4,5,6,7]

# Toca todas as notas e oitavas simultaneamente
play_notes(all_notes, all_octaves)
