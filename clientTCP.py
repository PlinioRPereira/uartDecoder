import socket
import json
import wave
import numpy as np

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
WAV_OUTPUT_FILENAME = "output.wav"

# Inicializando o socket TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Receber metadados do servidor
metadata_bytes = client_socket.recv(1024)
metadata = json.loads(metadata_bytes.decode('utf-8'))
RATE = metadata['rate']
CHANNELS = metadata['channels']
DTYPE = np.dtype(metadata['dtype'])  # Agora deve ser interpretável
BUFFER_SIZE = metadata['buffer_size']



# Inicializando o arquivo WAV
wav_file = wave.open(WAV_OUTPUT_FILENAME, 'wb')
wav_file.setnchannels(CHANNELS)
wav_file.setsampwidth(DTYPE.itemsize)
wav_file.setframerate(RATE)

print(f"Gravando com {RATE} taxa de amostragem, {CHANNELS} canais, buffer de tamanho {BUFFER_SIZE}.")

try:
    while True:
        audio_data = client_socket.recv(BUFFER_SIZE)
        if not audio_data:
            break
        wav_file.writeframes(audio_data)
except KeyboardInterrupt:
    print("Gravação interrompida pelo usuário.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
finally:
    wav_file.close()
    client_socket.close()
