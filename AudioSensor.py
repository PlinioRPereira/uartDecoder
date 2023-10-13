import sounddevice as sd
import numpy as np
import threading
import time  # Importação da biblioteca time para controle de tempo
import math
from datetime import datetime

RATE = 44100    # Taxa de amostragem
DTYPE = np.int16 # Tipo de dado
CHANNELS = 2    # Número de canais
DEVICE_ID = 0  # ID do dispositivo de entrada

class AudioSensor:
    def __init__(self):
        self.active = False
        self.thread = None
        self.data_array = []

    def list_audio_devices(self):
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"ID: {i}, Nome: {device['name']}, Canais: {device['max_input_channels']}")

    def startSensor(self,onStart,onData,onStop,timeout = 5):
        """Inicia a gravação do microfone"""
        self.active = True
        self.thread = threading.Thread(target=self._record,args=(onData,timeout))

        if onStart and callable(onStart):
            onStart(self.thread)
        self.thread.start()
        self.thread.join()  # Espera a thread terminar
        if onStop and callable(onStop):
            onStop(self.data_array,self.data_array)

    def stopSensor(self):
        """Para a gravação do microfone"""
        self.active = False
        print('STOP')

    def _record(self,onData,timeout):
        start_time = time.time()
        progressCount =0


        def onTransformData(indata, frames, time, status):
            # self.data_array.append([indata, frames, time, status])
            # self.print_callback_data(indata, frames, time, status)
            onData(indata[:, 0].astype(int), indata[:, 1].astype(int))

        with sd.InputStream(callback=onTransformData, channels=CHANNELS, samplerate=RATE, dtype=DTYPE, device=DEVICE_ID):
            while self.active:
                elapsed_time = time.time() - start_time
                progress = math.floor((elapsed_time / timeout) * 100);
                if progress != progressCount:
                    progressCount = progress;
                    print(progress, '%')
                # sd.sleep(timeout*1000)
                if elapsed_time > timeout:
                    self.active = False



