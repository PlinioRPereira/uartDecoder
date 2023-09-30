import sounddevice as sd
import numpy as np
import threading
import time  # Importação da biblioteca time para controle de tempo
import math
from datetime import datetime

RATE = 44100    # Taxa de amostragem
DTYPE = np.int16 # Tipo de dado
CHANNELS = 2    # Número de canais
DEVICE_ID = 17  # ID do dispositivo de entrada

class AudioSensor:
    def __init__(self):
        self.active = False
        self.thread = None
        self.data_array = []

    def printResultTable(self, title, byteObjArray, min_percent_over_threshold):
        # Imprimir o título
        print(f"Table Title: {title}\n")

        # Imprimir o cabeçalho da tabela
        print("{:<10} {:<20} {:<20} {:<10}".format('POS', 'VAL', '%', 'ACT-VAL'))

        # Imprimir os dados da tabela
        for i, obj in enumerate(byteObjArray):
            print("{:<10} {:<20} {:<20} {:<10}".format(
                obj[2],
                obj[3],
                f"{obj[4]}%",
                math.floor((obj[4]/min_percent_over_threshold)-1),
            ))

    def calculate_thresholds(self, gps_signal, confidence=95):
        alpha = 100 - (100 - confidence) / 2
        beta = (100 - confidence) / 2
        max_threshold = np.percentile(gps_signal, alpha)
        min_threshold = np.percentile(gps_signal, beta)
        return max_threshold, min_threshold
    def find_peaks(self,gps_signal, confidence=95, min_percent_over_threshold=10, sampleRate=500):
        max_threshold, min_threshold = self.calculate_thresholds(gps_signal, confidence)

        peak_intervals = []
        peak_start = None
        peak_value = None
        max_percent_over = 0
        max_percent_over_time = 0
        diff = 0

        # print("Threshold:", max_threshold,min_threshold)

        for i, sample in enumerate(gps_signal):
            is_peak = False


            # Check for positive peaks
            if sample > max_threshold and max_threshold != 0:
                diff = abs(sample - max_threshold)
                percent_over = (diff / max_threshold) * 100
                if max_percent_over < percent_over:
                    max_percent_over = percent_over
                    max_percent_over_time = i
                if percent_over >= min_percent_over_threshold:
                    is_peak = True

            # Check for negative peaks
            elif sample < min_threshold and min_threshold != 0:
                diff = abs(sample - min_threshold)
                percent_over = abs((diff / min_threshold)) * 100
                if max_percent_over < percent_over:
                    max_percent_over = percent_over
                    max_percent_over_time = i
                if percent_over >= min_percent_over_threshold:
                    is_peak = True

            if is_peak:
                if peak_start is None:
                    peak_start = i
                    peak_value = sample
                # No 'else' needed here since 'peak_start' will only be None at the beginning
            elif peak_start is not None:
                peak_end = i - 1
                max_peak_position = max_percent_over_time
                peak_intervals.append([peak_start, peak_end,max_peak_position, diff, max_percent_over])
                peak_start = None
                peak_end = None
                peak_value = None
                max_percent_over = 0

        return peak_intervals

    def filter_peaks(self,peak_intervals, x):
        if not peak_intervals:
            return []

        # Encontrar o menor e o maior valor de max_percent_over
        min_percent = min(peak[3] for peak in peak_intervals)
        max_percent = max(peak[3] for peak in peak_intervals)

        # Calcular o novo limite
        new_threshold = min_percent + (max_percent - min_percent) * x

        # Filtrar a lista de picos
        filtered_peaks = [peak for peak in peak_intervals if peak[3] > new_threshold]

        return filtered_peaks





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

    def print_callback_data(self,indata, frames, time, status):
        print("=== Callback Data ===")
        print("Indata: (Array de amostras de áudio)")
        print(indata)
        print(f"Frames: {frames}")
        print(f"Time Info: {time}")
        print(f"Status: {status}")
        print("=====================")

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



