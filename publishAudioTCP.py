import json
import sounddevice as sd
import numpy as np
import socket

def get_device_info(device_id):
    device_info = sd.query_devices(device_id, 'input')
    return device_info['default_samplerate'], np.int16

DEVICE_ID = 2  # ID do dispositivo de entrada
CHANNELS = 2  # Número de canais deve ser sempre 2
RATE, DTYPE = get_device_info(DEVICE_ID)
BUFFER_SIZE = 1024  # Tamanho do buffer

# Inicializando o socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5000))
server_socket.listen(1)
conn, addr = server_socket.accept()

print(f"Conexão estabelecida com {addr}")

# Enviar metadados para o cliente
metadata = {
    'rate': RATE,
    'channels': CHANNELS,
    'dtype': 'int16',  # Especifica o dtype como string
    'buffer_size': BUFFER_SIZE
}
conn.sendall(json.dumps(metadata).encode('utf-8'))

try:
    with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype=DTYPE, device=DEVICE_ID) as stream:
        while True:
            audio_chunk, overflowed = stream.read(BUFFER_SIZE)
            audio_bytes = audio_chunk.astype(DTYPE).tobytes()
            conn.sendall(audio_bytes)
except Exception as e:
    print(f"Ocorreu um erro: {e}")
finally:
    conn.close()
    server_socket.close()
