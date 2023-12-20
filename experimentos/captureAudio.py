import sounddevice as sd
import numpy as np
import wavio

# Parâmetros
RATE = 44100    # Taxa de amostragem
DTYPE = np.int16 # Tipo de dado
CHANNELS = 2    # Número de canais
SECONDS = 5     # Duração
DEVICE_ID = 17   # ID do dispositivo de entrada
FILENAME = "Audio2min_23a25hz.wav"

# Iniciar a gravação
print("Gravando...")
audio_data = sd.rec(int(SECONDS * RATE), samplerate=RATE, channels=CHANNELS, dtype=DTYPE, device=DEVICE_ID)
sd.wait()  # Aguardar o término da gravação
print("Gravação concluída.")
print("DATA",audio_data)


# Salvar como arquivo WAV
wavio.write(FILENAME, audio_data, RATE, sampwidth=2)
