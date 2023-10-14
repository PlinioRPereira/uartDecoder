import sounddevice as sd
import numpy as np
from flask import Flask, Response,render_template

app = Flask(__name__)

CHANNELS = 2  # Número de canais deve ser sempre 2
DEVICE_ID = 2  # ID do dispositivo de entrada

devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"ID: {i}, Nome: {device['name']}, Canais: {device['max_input_channels']},Taxas de amostragem suportadas: {device['default_samplerate']}")



# Obter informações do dispositivo para configurar taxa de amostragem e dtype
def get_device_info(device_id):
    device_info = sd.query_devices(device_id, 'input')
    return device_info['default_samplerate'], np.int16

RATE, DTYPE = get_device_info(DEVICE_ID)

devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"ID: {i}, Nome: {device['name']}, Canais: {device['max_input_channels']}, Taxa de amostragem padrão: {device['default_samplerate']}")

# Esta função gera um generator que captura áudio e o envia como bytes
def generate_audio():
    try:
        with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype=DTYPE, device=DEVICE_ID) as stream:
            while True:
                audio_chunk, overflowed = stream.read(1024)  # Ler 1024 amostras
                audio_bytes = audio_chunk.astype(DTYPE).tobytes()
                yield audio_bytes
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Esta rota permite ao cliente ouvir o áudio
@app.route('/audio')
def audio():
    return Response(generate_audio(), mimetype="audio/x-wav")


# Esta rota serve o HTML e as informações do dispositivo de áudio
@app.route('/')
def index():
    device_info = sd.query_devices(DEVICE_ID, 'input')
    audio_info = {
        'samplerate': RATE,
        'dtype': DTYPE,
        'channels': CHANNELS,
        'chunk_size': 1024,
        'device_name': device_info['name'],
    }
    return render_template('index.html', audio_info=audio_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
