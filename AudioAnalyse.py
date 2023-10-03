import wave
import array
import os
import math
import threading
import time
import asyncio
import concurrent.futures
import subprocess
import datetime  # Certifique-se de importar datetime
import json
import numpy as np
import csv
import pandas as pd
from UartDecoder import UartDecoder
from PeakFinder import PeakFinder
import copy


def calcular_tempo_aproximado(posicao, buffer=1024, framerate=44100):
    # Calcula o tempo aproximado em segundos
    tempo_aproximado = (posicao * buffer) / framerate

    # Converte o tempo para minutos, segundos e milissegundos
    minutos = int(tempo_aproximado // 60)
    segundos = int(tempo_aproximado % 60)
    milissegundos = int((tempo_aproximado * 1000) % 1000)

    # Preenche com zeros à esquerda para ter pelo menos 2 dígitos
    minutos_str = str(minutos).zfill(2)
    segundos_str = str(segundos).zfill(2)

    # Preenche com zeros à direita para ter exatamente 3 dígitos em milissegundos
    milissegundos_str = str(milissegundos)
    milissegundos_str = milissegundos_str.ljust(3, '0')

    return f"{minutos_str}:{segundos_str}:{milissegundos_str}"

def format_tempo_aproximado(tempo_aproximado):
    # Converte o tempo para minutos, segundos e milissegundos
    minutos = int(tempo_aproximado // 60)
    segundos = int(tempo_aproximado % 60)
    milissegundos = int((tempo_aproximado * 1000) % 1000)

    # Preenche com zeros à esquerda para ter pelo menos 2 dígitos
    minutos_str = str(minutos).zfill(2)
    segundos_str = str(segundos).zfill(2)

    # Preenche com zeros à direita para ter exatamente 3 dígitos em milissegundos
    milissegundos_str = str(milissegundos)
    milissegundos_str = milissegundos_str.ljust(3, '0')

    return f"{minutos_str}:{segundos_str}:{milissegundos_str}"


class WaveReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.wav_file = wave.open(self.file_path, 'rb')
        self.num_channels = self.wav_file.getnchannels()
        self.sample_width = self.wav_file.getsampwidth()
        self.frame_count = self.wav_file.getnframes()
        self.sample_rate = self.wav_file.getframerate()

    def calculate_q_factor(self,freqs, fft_magnitude):
        # Encontrar a frequência de ressonância (frequência com amplitude máxima)
        f_res = freqs[np.argmax(fft_magnitude)]

        # Encontrar a amplitude máxima
        max_magnitude = np.max(fft_magnitude)

        # Encontrar as frequências onde a magnitude é 1/sqrt(2) da magnitude máxima
        half_power_points = np.where(fft_magnitude >= max_magnitude / np.sqrt(2))[0]

        # Calcular a largura de banda (Delta f)
        if len(half_power_points) > 1:
            delta_f = freqs[half_power_points[-1]] - freqs[half_power_points[0]]
        else:
            return -1

        # Calcular e retornar o Fator de Qualidade (Q)
        Q = f_res / delta_f
        return Q

    def calculate_fft(self,data, n_fft=None):
        """
        Calcula a Transformada Rápida de Fourier (FFT) do array de dados fornecido.

        Parâmetros:
        - data: array de números representando o sinal.
        - sampling_rate: taxa de amostragem do sinal.
        - n_fft: número de pontos FFT. Se None, será usado o tamanho do array de dados.

        Retorna:
        - freqs: array com as frequências correspondentes.
        - fft_values: array com as magnitudes dos valores da FFT.
        - fft_phase: array com as fases dos valores da FFT.
        """


        # Tamanho do sinal
        N = len(data)

        # Número de pontos FFT
        if n_fft is None:
            n_fft = N

        # Calculando FFT usando NumPy
        fft_values = np.fft.fft(data, n=n_fft)

        # Normalizando os valores da FFT
        fft_values = fft_values[:n_fft // 2] / n_fft

        # Pegando a magnitude dos valores da FFT
        fft_magnitude = np.abs(fft_values)

        # Pegando a fase dos valores da FFT
        fft_phase = np.angle(fft_values)

        # Calculando as frequências correspondentes
        freqs = np.fft.fftfreq(n_fft, 1 / self.sample_rate)[:n_fft // 2]

        Q = self.calculate_q_factor(freqs, fft_magnitude)

        return freqs, fft_magnitude, fft_phase, Q

    def getChannel(self, channel_index):
        if channel_index >= self.num_channels or channel_index < 0:
            raise ValueError("Invalid channel index")

        self.wav_file.rewind()
        raw_data = self.wav_file.readframes(self.frame_count)

        channel_data = array.array("h")

        for i in range(channel_index, len(raw_data), self.sample_width * self.num_channels):
            sample = int.from_bytes(raw_data[i:i + self.sample_width], byteorder='little', signed=True)
            channel_data.append(sample)

        return channel_data


    def getFFTValues(self,channel_index,n_fft=1024):
        data = self.getChannel(channel_index)
        # Número total de blocos
        num_blocks = len(data) // n_fft

        # Armazenar FFT de cada bloco
        blocks = []

        for i in range(num_blocks):
            start_idx = i * n_fft
            end_idx = (i + 1) * n_fft
            block = data[start_idx:end_idx]
            freqs, fft_values, phase, Q = self.calculate_fft(block)
            blocks.append([freqs, fft_values, phase, Q])

        return blocks



    def calculate_thresholds(self, audio_signal, confidence=95):
        alpha = 100 - (100 - confidence) / 2
        beta = (100 - confidence) / 2
        max_threshold = np.percentile(audio_signal, alpha)
        min_threshold = np.percentile(audio_signal, beta)
        return max_threshold, min_threshold



    def get_peak_time(self, sampleIdx, sampleRate):
        rawTimeValue = (sampleIdx*1024) / sampleRate  # Note que é uma divisão aqui
        # print("rawTimeValue:", rawTimeValue)
        #
        # segundos = int(rawTimeValue)
        # milisegundos = ((rawTimeValue - segundos) * 1000)
        # time = datetime.timedelta(seconds=segundos, milliseconds=milisegundos)
        return rawTimeValue

    def find_peaks(self, audio_signal, confidence=95, min_percent_over_threshold=10, sampleRate=500):
        max_threshold, min_threshold = self.calculate_thresholds(audio_signal, confidence)

        peak_intervals = []
        peak_start = None
        peak_value = None
        max_percent_over = 0
        max_percent_over_time = 0
        diff = 0

        # print("Threshold:", max_threshold,min_threshold)

        for i, sample in enumerate(audio_signal):
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
                peak_start_time = (peak_start*1024/44100)
                peak_end_time = (peak_end*1024/44100)
                peak_intervals.append([peak_start, peak_end, max_peak_position, diff, max_percent_over,peak_start_time,peak_end_time])
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


    def find_incoherent_phases(self,phase_array, std_multiplier=2.1413):
        """
        Encontra pontos e frequências de incoerência na matriz de fases.

        Parâmetros:
        - phase_array: array 2D onde cada linha é um conjunto de fases para todas as frequências em um ponto no tempo.
        - std_multiplier: O número de desvios padrão usado para definir um valor como incoerente.

        Retorna:
        - incoherent_indices: Uma lista de arrays, onde o primeiro elemento é o índice do cálculo FFT e o segundo é uma lista com os índices das frequências incoerentes.
        """
        # Calcular a média e o desvio padrão das fases para cada frequência
        mean_phases = np.mean(phase_array, axis=0)
        std_phases = np.std(phase_array, axis=0)

        incoherent_indices = []

        # Verificar cada conjunto de fases para ver se ele é incoerente
        for i, phases in enumerate(phase_array):
            deviation = np.abs(phases - mean_phases)
            freq_indices = np.where(deviation > std_multiplier * std_phases)[0]

            if len(freq_indices) > 0:
                incoherent_indices.append([i, list(freq_indices)])

        return incoherent_indices

    def getValuesByFreqIndex(self, dataFreqs, index):
        """
        Obtém os valores de uma frequência específica de um array 2D (cada linha representa uma transformada FFT).

        Parâmetros:
        - dataFreqs: array 2D que armazena os valores FFT.
        - index: índice da frequência desejada.

        Retorna:
        - freq_values: array com os valores da frequência especificada ao longo do tempo.
        """
        freq_values = [freqs[index] for freqs in dataFreqs]
        return freq_values

    def iterateAndAnalysisFreqValues(self,dataFreqs, channelName, freqsList,confidence=99,fator_filtro=0.80,min_percent_over_threshold=80):
        """
        Itera por todos os índices de frequência e imprime os valores correspondentes.

        Parâmetros:
        - dataFreqs: array 2D que armazena os valores FFT.
        """

        result = []

        num_freqs = len(dataFreqs[0])  # supõe que todas as linhas tenham o mesmo número de colunas
        for index in range(num_freqs):
            freq_values = self.getValuesByFreqIndex(dataFreqs, index)

            # print('dynamicMin_percent_over_threshold',dynamicMin_percent_over_threshold)
            peaksFreq = self.find_peaks(freq_values, confidence, min_percent_over_threshold)
            filtered_peaksFreq = self.filter_peaks(peaksFreq, fator_filtro)
            if filtered_peaksFreq is not None and isinstance(filtered_peaksFreq, list) and len(
                    filtered_peaksFreq) > 0:
                result.append(
                    [filtered_peaksFreq, min_percent_over_threshold, channelName, index, freqsList[index]])
            else:
                result.append(None)

        return result

    def printResultTable(self,listOfResult,dataQ,incoherent_indices_phases):

        allPeaks = []
        # Função para a chave de ordenação
        def sort_key(obj):
            return obj[2]

        # Imprimir o título
        print(f"Resultado: \n")

        # Imprimir o cabeçalho da tabela
        print("{:<10} {:<25} {:<10} {:<20} {:<20} {:<20} {:<5} {:<5} {:<20} {:<10} {:<10} {:<10}".format('POS','TIME', 'SIZE', 'VAL',
                                                                                                  '%', 'ACT-VAL', 'CH',
                                                                                                  'FREQNum',
                                                                                                  'FREQValue', 'FRAME',
                                                                                                  'iPhase', 'QFactor'))

        for iResult, result in enumerate(listOfResult):
            if not result or not result[0]:
                continue

            peakList = result[0]
            min_percent_over_threshold = result[1]
            channelName = result[2]
            indexFreq = result[3]
            freqValue = result[4]


            sorted_peakList = sorted(peakList, key=sort_key)

            for i, obj in enumerate(sorted_peakList):
                hasIncoherentPhase = obj[2] in incoherent_indices_phases

                if dataQ[obj[2]] <10:
                    continue

                allPeaks.append(obj)

                print("{:<10} {:<25} {:<10} {:<20} {:<20} {:<20} {:<5} {:<5} {:<20} {:<10} {:<10} {:<10}".format(
                    obj[2],
                    f"{calcular_tempo_aproximado(obj[2])}-{calcular_tempo_aproximado(obj[2]+1)}",
                    obj[1] - obj[0],
                    obj[3],
                    f"{obj[4]}%",
                    math.floor((obj[4] / min_percent_over_threshold) - 1),
                    channelName,
                    indexFreq,
                    freqValue,
                    obj[2],
                    hasIncoherentPhase,
                    dataQ[obj[2]]
                ))

        return sorted(allPeaks, key=sort_key)


    def getCompleteResult(self,channel_index=0):
        allData = self.getFFTValues(channel_index)
        freqs = [subarray[0] for subarray in allData][0]
        fft_values = [subarray[1] for subarray in allData]
        phases = [subarray[2] for subarray in allData]
        QFactors = [subarray[3] for subarray in allData]
        incoherent_indices_phases = self.find_incoherent_phases(phases)
        peaksResults = self.iterateAndAnalysisFreqValues(fft_values,channel_index,freqs);
        return self.printResultTable(peaksResults,QFactors,incoherent_indices_phases)

    def getDetail(self):
        """
        Retorna um dicionário contendo detalhes do arquivo de áudio WAV carregado. As propriedades incluem:
        - 'file_size': Tamanho do arquivo em bytes
        - 'file_extension': Extensão do arquivo
        - 'num_channels': Número de canais
        - 'sample_width': Largura da amostra em bytes
        - 'frame_count': Número total de frames
        - 'sample_rate': Taxa de amostragem em Hz (frames por segundo)
        - 'duration': Duração do áudio em segundos
        """
        file_size = os.path.getsize(self.file_path)
        file_extension = os.path.splitext(self.file_path)[1]
        duration = self.frame_count / float(self.sample_rate)

        return {
            'file_size': file_size,
            'file_extension': file_extension,
            'num_channels': self.num_channels,
            'sample_width': self.sample_width,
            'frame_count': self.frame_count,
            'sample_rate': self.sample_rate,
            'duration': duration
        }

    def close(self):
        self.wav_file.close()


utils = PeakFinder()


#---UTIL----------------------------------------------------------------------------
def format_peak( i, peak):

    start_time = format_tempo_aproximado(peak[5])
    end_time =format_tempo_aproximado(peak[6])
    percent_over = "{:.2f}%".format(peak[4])

    # Verificar se start_time é igual a end_time
    if start_time == end_time:
        time_str = f"{start_time} - {format_tempo_aproximado((peak[1]+1)*1024/44100)}"
    else:
        time_str = f"{start_time} - {end_time}"

    formatted_peak = [
        f'Pico {i + 1}',
        percent_over,
        time_str
    ]

    return formatted_peak

def find_intersection(peaks, decoded_data):
    intersected_data = []

    for i, peak in enumerate(peaks):
        peak_start, peak_end = (peak[0]*1024/44100), (peak[1]*1024/44100)

        for data in decoded_data:
            data_start = data.beginSample  # Acesso correto ao atributo
            data_end = data.endSample  # Acesso correto ao atributo

            if data_start is None or data_end is None:
                continue  # Pular para a próxima iteração se algum valor for None

            # Verifica a interseção entre os intervalos de pico e dados
            if data_start <= peak_end and data_end >= peak_start:
                data_copy = copy.copy(data)
                data_copy.peak = format_peak(i, peak)
                intersected_data.append(data_copy)

    return intersected_data

#---///UTIL----------------------------------------------------------------------------


# Uso
audioPath = "experimentos/test-exp1.wav"  # Coloque o caminho do seu arquivo WAV aqui
reader = WaveReader(audioPath)
decoder = UartDecoder(audioPath)

print("Anaĺisando o arquivo ",audioPath)

print("Extraindo canais de audio e preparando a sequencia de Gray...")
decoded_data = decoder.decode(1)

try:
    details = reader.getDetail()
    print(details)
    peaks = reader.getCompleteResult()

    print("Total de Picos:", len(peaks) )

    selectedBytes = find_intersection(peaks, decoded_data)
    num_elements = len(selectedBytes)
    print(f"Foram selecionados {num_elements} bytes da sequencia de Gray")
    utils.printtable(selectedBytes)
    print('BIN:',utils.extractBinarySequence(selectedBytes))
    print('CHAR(Gray):',utils.extractChrSequence(selectedBytes))
    print('CHAR(BIN):',utils.extractChar2Sequence(selectedBytes))
    print('CHAR(PT-BR):',utils.extractPortugueseSequence(selectedBytes))




finally:
    reader.close()
