import numpy as np
import datetime

portuguese_chars = [
    # Alfabeto básico
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',

    # Números
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',

    # Acentuações e caracteres especiais
    'á', 'à', 'â', 'ã', 'ä', 'é', 'è', 'ê', 'ë', 'í', 'ì', 'î', 'ï',
    'ó', 'ò', 'ô', 'õ', 'ö', 'ú', 'ù', 'û', 'ü', 'ç',
    'Á', 'À', 'Â', 'Ã', 'Ä', 'É', 'È', 'Ê', 'Ë', 'Í', 'Ì', 'Î', 'Ï',
    'Ó', 'Ò', 'Ô', 'Õ', 'Ö', 'Ú', 'Ù', 'Û', 'Ü', 'Ç',

    # Sinais de pontuação e outros símbolos
    '.', ',', ';', ':', '!', '?', '-', '+',
    '@', '$', '%', '^', '&', '*', '=', '<', '>',
    '”', '‘', '#'
]

class PeakFinder:

    def calculate_thresholds(self, audio_signal, confidence=95):
        alpha = 100 - (100 - confidence) / 2
        beta = (100 - confidence) / 2
        max_threshold = np.percentile(audio_signal, alpha)
        min_threshold = np.percentile(audio_signal, beta)
        return max_threshold, min_threshold

    def get_peak_time(self, sampleIdx, sampleRate):
        rawTimeValue = sampleIdx / sampleRate  # Note que é uma divisão aqui
        # print("rawTimeValue:", rawTimeValue)
        #
        # segundos = int(rawTimeValue)
        # milisegundos = ((rawTimeValue - segundos) * 1000)
        # time = datetime.timedelta(seconds=segundos, milliseconds=milisegundos)
        return rawTimeValue

    def format_peaks(self,peaks):
        formatted_peaks = []
        for i, peak in enumerate(peaks):
            start_time = "{:.4f}".format(peak[4])
            end_time = "{:.4f}".format(peak[5])
            formatted_peak = [
                f'Pico {i + 1}',
                start_time,
                end_time
            ]
            formatted_peaks.append(formatted_peak)
        return formatted_peaks

    def find_peaks(self, audio_signal, confidence=95, min_percent_over_threshold=10, sampleRate=44100):
        max_threshold, min_threshold = self.calculate_thresholds(audio_signal, confidence)

        peak_intervals = []
        peak_start = None
        peak_value = None

        print("find_peaks:", max_threshold,min_threshold)

        for i, sample in enumerate(audio_signal):
            is_peak = False

            # Check for positive peaks
            if sample > max_threshold:
                diff = abs(sample - max_threshold)
                percent_over = (diff / max_threshold) * 100
                if percent_over >= min_percent_over_threshold:
                    is_peak = True

            # Check for negative peaks
            elif sample < min_threshold:
                diff = abs(sample - min_threshold)
                percent_over = abs((diff / min_threshold)) * 100
                if percent_over >= min_percent_over_threshold:
                    is_peak = True

            if is_peak:
                if peak_start is None:
                    peak_start = i
                    peak_value = sample
                # No 'else' needed here since 'peak_start' will only be None at the beginning
            elif peak_start is not None:
                peak_end = i - 1
                peak_start_time = self.get_peak_time(peak_start, sampleRate)
                peak_end_time = self.get_peak_time(peak_end, sampleRate)
                peak_intervals.append([peak_start, peak_end, diff, percent_over, peak_start_time, peak_end_time])
                peak_start = None
                peak_end = None
                peak_start_time = None
                peak_end_time = None
                peak_value = None

        return peak_intervals

    def find_intersection(self, peaks, decoded_data):
        intersected_data = []

        for peak in peaks:
            peak_start, peak_end = peak[0], peak[1]

            for data in decoded_data:
                data_start = data.beginSample  # Acesso correto ao atributo
                data_end = data.endSample  # Acesso correto ao atributo

                if data_start is None or data_end is None:
                    continue  # Pular para a próxima iteração se algum valor for None

                # Verifica a interseção entre os intervalos de pico e dados
                if data_start <= peak_end and data_end >= peak_start:
                    intersected_data.append(data)

        return intersected_data

    def printByteObjArray(self,byteObjArray):
        for byte in byteObjArray:
            print("{",
                  f"value={byte.value}, chr={chr(byte.value)}, binaryStr={byte.binaryStr}, beginSample={byte.beginSample}, endSample={byte.endSample}, beginCluster={byte.beginCluster}",
                  "}")

    # Método para extrair a sequência de caracteres da propriedade "chr"
    def extractChrSequence(self,byteObjArray):
        return ''.join([chr(byte.value) for byte in byteObjArray])

    # Método para extrair a sequência de bytes binários da propriedade "binaryStr"
    def extractBinarySequence(self,byteObjArray):
        return ' '.join([byte.binaryStr for byte in byteObjArray])

    def extractChar2Sequence(self, byteObjArray):
        return ''.join([chr(int(byte.binaryStr, 2)) for byte in byteObjArray])

    def extractPortugueseSequence(self,byteObjArray):
        return ''.join([portuguese_chars[byte.value % len(portuguese_chars)] for byte in byteObjArray])







