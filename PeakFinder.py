import numpy as np
from scipy.fftpack import fft
import copy

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
    PeakStruct = type("PeakStruct", (),
        {"start": None, "end": None, "diff": None, "maxValuePercentual": None, "maxValueTime": None, "startTime": None, "endTime": None })

    def calculate_thresholds(self, audio_signal, confidence=95):
        alpha = 100 - (100 - confidence) / 2  #Eg. 97,5
        beta = (100 - confidence) / 2         #Eg. 2.5  
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

    def format_peak(self, i, peak):
        start_time = "{:.4f}s".format(peak[4])
        end_time = "{:.4f}s".format(peak[5])
        percent_over = "{:.2f}%".format(peak[3])

        # Verificar se start_time é igual a end_time
        if start_time == end_time:
            time_str = start_time  # Mostre apenas start_time
        else:
            time_str = f"{start_time} - {end_time}"

        formatted_peak = [
            f'Pico {i + 1}',
            percent_over,
            time_str
        ]
        return formatted_peak
    
    def format_peaks(self, peaks):
        formatted_peaks = []
        for i, peak in enumerate(peaks):
            start_time = "{:.4f}s".format(peak[4])
            end_time = "{:.4f}s".format(peak[5])
            percent_over = "{:.2f}%".format(peak[3])

            # Verificar se start_time é igual a end_time
            if start_time == end_time:
                time_str = start_time  # Mostre apenas start_time
            else:
                time_str = f"{start_time} - {end_time}"

            formatted_peak = [
                f'Pico {i + 1}',
                percent_over,
                time_str
            ]
            formatted_peaks.append(formatted_peak)
        
        return formatted_peaks

    def find_harmonic_variations(self, audio_signal, sampleRate=44100, percent_threshold=10):
        harmonic_moments = []  # Armazena os momentos em que ocorrem variações harmônicas
        fundamental_freq = None

        # Step size for Fourier Transform
        N = 1024

        for i in range(0, len(audio_signal) - N, N):
            # Perform FFT to get frequency components
            fft_values = np.fft.fft(audio_signal[i:i + N])
            freqs = np.fft.fftfreq(len(fft_values), 1 / sampleRate)

            # Take only the positive frequencies
            positive_freq_idxs = np.where(freqs > 0)
            positive_freqs = freqs[positive_freq_idxs]
            positive_fft_values = np.abs(fft_values[positive_freq_idxs])

            # Find the dominant frequency
            dominant_frequency = positive_freqs[np.argmax(positive_fft_values)]

            # Initialize fundamental_freq if it is None
            if fundamental_freq is None:
                fundamental_freq = dominant_frequency
            else:
                if fundamental_freq != 0:  # Check if fundamental frequency is not zero
                    # Calculate the closest harmonic to the dominant frequency
                    closest_harmonic = fundamental_freq * np.round(dominant_frequency / fundamental_freq)

                    if closest_harmonic != 0:  # Avoid division by zero
                        # Calculate the percent difference from the closest harmonic
                        percent_diff = abs((dominant_frequency - closest_harmonic) / closest_harmonic) * 100

                        # Check if the percent difference exceeds the threshold
                        if percent_diff > percent_threshold:
                            moment_time = i / sampleRate
                            harmonic_moments.append(
                                [i, fundamental_freq, dominant_frequency, moment_time])
                            fundamental_freq = dominant_frequency  # Update the fundamental frequency
                else:
                    fundamental_freq = dominant_frequency  # Update if the fundamental frequency was zero

        return harmonic_moments

    def find_frequency_peaks(self, audio_signal, sampleRate=44100, threshold_percent=10):
        frequency_intervals = []
        freq_start = None
        freq_value = None

        # Step size for Fourier Transform
        N = 1024

        for i in range(0, len(audio_signal) - N, N):
            # Perform FFT to get frequency components
            fft_values = fft(audio_signal[i:i + N])
            freqs = np.fft.fftfreq(len(fft_values), 1 / sampleRate)

            # Take only the positive frequencies
            positive_freq_idxs = np.where(freqs > 0)
            positive_freqs = freqs[positive_freq_idxs]
            positive_fft_values = np.abs(fft_values[positive_freq_idxs])

            # Find the dominant frequency
            dominant_frequency = positive_freqs[np.argmax(positive_fft_values)]

            if freq_start is None:
                freq_start = i
                freq_value = dominant_frequency
            else:
                # Calculate the percent change in frequency
                percent_change = ((dominant_frequency - freq_value) / freq_value) * 100

                # Check for sudden change in frequency
                if abs(percent_change) >= threshold_percent:
                    freq_end = i
                    freq_start_time = freq_start / sampleRate
                    freq_end_time = freq_end / sampleRate
                    frequency_intervals.append(
                        [freq_start, freq_end, freq_value, dominant_frequency, freq_start_time, freq_end_time])
                    freq_start = i
                    freq_value = dominant_frequency

        return frequency_intervals
    
    def find_peaks_region(self, audio_signal, confidence=95, min_percent_over_threshold=10, sampleRate=44100):
        max_threshold, min_threshold = self.calculate_thresholds(audio_signal, confidence)

        peakIntervals = []
        peak_start = None
        peak_value = None
        max_percent_over = 0

        print("Threshold:", max_threshold,min_threshold)

        for i, sample in enumerate(audio_signal):
            is_peak = False


            # Check for positive peaks
            if sample > max_threshold:
                diff = abs(sample - max_threshold)
                percent_over = (diff / max_threshold) * 100
                if max_percent_over < percent_over:
                    max_percent_over = percent_over
                if percent_over >= min_percent_over_threshold:
                    is_peak = True

            # Check for negative peaks
            elif sample < min_threshold:
                diff = abs(sample - min_threshold)
                percent_over = abs((diff / min_threshold)) * 100
                if max_percent_over < percent_over:
                    max_percent_over = percent_over
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
                peakIntervals.append([peak_start, peak_end, diff, max_percent_over, peak_start_time, peak_end_time])
                peak_start = None
                peak_end = None
                peak_start_time = None
                peak_end_time = None
                peak_value = None
                max_percent_over = 0

        return peakIntervals
    
    def find_peaks(self, audio_signal, confidence=95, min_percent_over_threshold=10, sampleRate=44100):
        max_threshold, min_threshold = self.calculate_thresholds(audio_signal, confidence)

        peakArray = []
        peak_start = None
        max_percent_over = 0
        max_percent_over_sample = 0

        print("Threshold:", max_threshold, min_threshold)

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

            if (sample < min_threshold or sample > max_threshold) and max_percent_over < percent_over:                
                max_percent_over = percent_over
                max_percent_over_sample = i

            if is_peak:
                if peak_start is None:
                    peak_start = i                    

            elif peak_start is not None:
                peak = self.PeakStruct() 
                peak.start = peak_start
                peak.end = i - 1
                peak.diff = diff
                peak.maxValuePercentual = max_percent_over
                peak.maxValueTime = self.get_peak_time(max_percent_over_sample, sampleRate) 
                peak.startTime = self.get_peak_time(peak_start, sampleRate)
                peak.endTime = self.get_peak_time(peak.end, sampleRate)
                peakArray.append(peak)

                peak_start = None
                max_percent_over = 0

        return peakArray

    def filter_peaks(self, peakIntervals, x):
        if not peakIntervals:
            return []

        # Encontrar o menor e o maior valor de max_percent_over
        min_percent = min(peak[3] for peak in peakIntervals)
        max_percent = max(peak[3] for peak in peakIntervals)

        # Calcular o novo limite
        new_threshold = min_percent + (max_percent - min_percent) * x

        # Filtrar a lista de picos
        filtered_peaks = [peak for peak in peakIntervals if peak[3] > new_threshold]

        return filtered_peaks

    def find_intersection(self, peaks, decoded_data):
        intersected_data = []

        for i, peak in enumerate(peaks):
            peak_start, peak_end = peak[0], peak[1]

            for data in decoded_data:
                data_start = data.beginSample  # Acesso correto ao atributo
                data_end = data.endSample  # Acesso correto ao atributo

                if data_start is None or data_end is None:
                    continue  # Pular para a próxima iteração se algum valor for None

                # Verifica a interseção entre os intervalos de pico e dados
                if data_start <= peak_end and data_end >= peak_start:
                    data_copy = copy.copy(data)
                    data_copy.peak = self.format_peak(i, peak)
                    intersected_data.append(data_copy)

        return intersected_data

    def printtable(self, byteObjArray):
        print(
            "{:<10} {:<10} {:<10} {:<10} {:<10} {:<15} {:<10} {:<15}".format('BIN', 'NUM', 'CHR(GRAY)', 'CHR(BIN)', 'MAP(PT_BR)', 'PICO', '%',
                                                                            'TEMPO'))

        for byte in byteObjArray:
            print("{:<10} {:<10} {:<10} {:<10} {:<10} {:<15} {:<10} {:<15}".format(
                byte.binaryStr,
                byte.value,
                chr(byte.value),
                chr(int(byte.binaryStr, 2)),
                portuguese_chars[byte.value % len(portuguese_chars)],
                byte.peak[0],
                f"{byte.peak[1]}%",
                f"{byte.peak[2]}s"
            ))
            
    def printPeaks(self, peakArray):        
        print("{:<10} {:<10} {:<10} {:<10} {:<15} {:<15} {:<15}".format('start', 'end', 'diff', 'peak (%)', 'maxPeak Time', 'start time', 'stop time'))
        for peak in peakArray:
            print("{:<10} {:<10} {:<10} {:<10} {:<15} {:<15} {:<15}".format(
                peak.start,
                peak.end,
                peak.diff,
                round(peak.maxValuePercentual, 2),
                round(peak.maxValueTime, 6),                
                round(peak.startTime, 6),
                round(peak.endTime, 6)
            ))

    def printByteObjArray(self,byteObjArray):
        for byte in byteObjArray:
            print("{",
                    f"value={byte.value}, chr={chr(byte.value)}, binaryStr={byte.binaryStr}, beginSample={byte.beginSample},peak={byte.peak[0]}, endSample={byte.endSample}, beginCluster={byte.beginCluster}",
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

    def find_mismatches(self,left_channel, right_channel):
        """
        This function takes two arrays of binarized audio signals (left_channel and right_channel)
        and returns an array containing the indices where the signals do not match.

        Parameters:
            left_channel (array): Binarized audio signal for the left channel (array of 0s and 1s).
            right_channel (array): Binarized audio signal for the right channel (array of 0s and 1s).

        Returns:
            mismatch_indices (array): Indices where the signals do not match.
        """

        # Initialize an empty list to store the indices where mismatches occur
        mismatch_indices = []

        # Check that the lengths of the two channels are the same
        if len(left_channel) != len(right_channel):
            return "The lengths of the two channels must be the same."

        # Loop through the arrays to find where the signals do not match
        for i in range(len(left_channel)):
            if left_channel[i] != right_channel[i]:
                mismatch_indices.append(i)

        return np.array(mismatch_indices)







