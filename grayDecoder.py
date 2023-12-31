import wave
import numpy as np

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


class TVCUtils:

    def calculate_thresholds(self, audio_signal, confidence=95):
        alpha = 100 - (100 - confidence) / 2
        beta = (100 - confidence) / 2
        max_threshold = np.percentile(audio_signal, alpha)
        min_threshold = np.percentile(audio_signal, beta)
        return max_threshold, min_threshold

    def find_peaks(self, audio_signal, confidence=95, min_percent_over_threshold=10):
        max_threshold, min_threshold = self.calculate_thresholds(audio_signal, confidence)

        peak_intervals = []
        peak_start = None
        peak_value = None

        for i, sample in enumerate(audio_signal):
            diff = abs(sample - max_threshold) if sample > max_threshold else abs(sample - min_threshold)
            percent_over = (diff / max_threshold) * 100 if sample > max_threshold else (diff / min_threshold) * 100

            is_peak = False
            if percent_over >= min_percent_over_threshold:
                if sample > max_threshold or sample < min_threshold:
                    is_peak = True

            if is_peak:
                if peak_start is None:
                    peak_start = i
                    peak_value = sample
                # No 'else' needed here since 'peak_start' will only be None at the beginning
            elif peak_start is not None:
                peak_end = i - 1
                peak_intervals.append([peak_start, peak_end, diff, percent_over])
                peak_start = None
                peak_value = None

        return peak_intervals

    def find_intersection(self,peaks, decoded_data):
        intersected_data = []

        for peak in peaks:
            peak_start, peak_end = peak[0], peak[1]

            for data in decoded_data:
                data_start = data.beginSample  # Acesso correto ao atributo
                data_end = data.endSample  # Acesso correto ao atributo

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


class UartDecoder:
    def __init__(self, file_path, threshold=0, samplesQtdToCalcThreshold=100, raiseAndFallEdgesQtd=20000):
        self.file_path = file_path
        self.left_channel, self.right_channel = self.open_uart_wav()  # Removido o argumento adicional
        self.threshold = threshold
        self.samplesQtdToCalcThreshold = samplesQtdToCalcThreshold
        self.raiseAndFallEdgesQtd = raiseAndFallEdgesQtd

    def open_uart_wav(self):  # Adicionado 'self' aqui
        wav = wave.open(self.file_path, 'rb')  # Usando self.file_path diretamente

        # Obtém os parâmetros do arquivo WAV
        num_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        num_frames = wav.getnframes()

        # Lê todos os quadros de áudio
        frames = wav.readframes(num_frames)

        # Converte os quadros em um array NumPy
        audio_data = np.frombuffer(frames, dtype=np.int16)

        # Separa os canais esquerdo e direito
        if num_channels == 2:
            left_channel = audio_data[::2]
            right_channel = audio_data[1::2]
        else:
            left_channel = audio_data
            right_channel = None
        # print("Left Channel:", left_channel)
        # print("Right Channel:", right_channel)
        return left_channel, right_channel

    def binarize(self, channelData):  # Adicionado 'self' aqui
        binary_array = [1 if sample > self.threshold else 0 for sample in
                        channelData]  # Usando self.threshold diretamente
        return binary_array

    def autoThresholdBinarization(self,samples):
        binary_array = []
        windowSize = self.samplesQtdToCalcThreshold;


        for i in range(0, len(samples), windowSize):
            window = samples[i:i + windowSize]
            threshold = (max(window) + min(window)) / 2

            binarized_window = [1 if sample >= threshold else 0 for sample in window]
            binary_array.extend(binarized_window)

        return binary_array

    def findTransmitionWindow(self,binary_array):
        window_start = None
        window_end = None
        transitions = 0
        startPrefixSamplesQtd = 50  # Add 50 samples before window_start to facilitate decoding

        for i in range(len(binary_array) - 1):
            if binary_array[i] != binary_array[i + 1]:
                transitions += 1

                if transitions == 1:
                    window_start = i

                if transitions == self.raiseAndFallEdgesQtd:
                    window_end = i
                    break

        if (window_start > startPrefixSamplesQtd):
            window_start = window_start - startPrefixSamplesQtd

        return window_start, window_end

    def calculate_average_length(self,array, x):
        total = 0
        count = 0

        for num in array:
            if num in (x - 1, x, x + 1):
                total += num
                count += 1

        if count > 0:
            average = total / count
            return average
        else:
            return None

    def calcBitAverageLength(self,binary_array, window_start, window_end):
        zeros_lengths = []
        ones_lengths = []
        current_length = 0
        current_value = None

        for i in range(window_start, window_end + 1):
            if current_value is None:
                current_value = binary_array[i]
                current_length = 1
            elif binary_array[i] == current_value:
                current_length += 1
            else:
                if current_length >= 3:
                    if current_value == 0:
                        zeros_lengths.append(current_length)
                    else:
                        ones_lengths.append(current_length)
                current_value = binary_array[i]
                current_length = 1

        if current_length >= 3:
            if current_value == 0:
                zeros_lengths.append(current_length)
            else:
                ones_lengths.append(current_length)

        zero_min_length = self.calculate_average_length(zeros_lengths, min(zeros_lengths) if zeros_lengths else 0)
        one_min_length = self.calculate_average_length(ones_lengths, min(ones_lengths) if ones_lengths else 0)

        return zero_min_length, one_min_length

    def generateUartBitStream(self,binary_array, zeroBitLength, oneBitLength, beginSampleOffest):
        BitCluster = type("BitCluster", (),
                          {"value": None, "length": None, "samplesQtd": None, "rest": None, "beginSample": None})
        output_array = []
        current_value = None
        current_length = 0
        beginSample = beginSampleOffest

        for i in range(len(binary_array)):
            if current_value is None:
                current_value = binary_array[i]
                current_length = 1
                beginSample = i
            elif binary_array[i] == current_value:
                current_length += 1
            else:
                bit_cluster = BitCluster()
                if current_value == 1:
                    bitLength = oneBitLength
                else:
                    bitLength = zeroBitLength
                approximate_multiples = round(current_length / bitLength)
                rest = abs(current_length - (approximate_multiples * bitLength)) / bitLength

                bit_cluster.value = current_value
                bit_cluster.length = approximate_multiples
                bit_cluster.samplesQtd = current_length
                bit_cluster.rest = rest
                bit_cluster.beginSample = beginSample
                output_array.append(bit_cluster)

                current_value = binary_array[i]
                beginSample = i
                current_length = 1

        bit_cluster = BitCluster()
        bit_cluster.value = current_value
        bit_cluster.length = round(current_length / bitLength)
        bit_cluster.samplesQtd = current_length
        bit_cluster.rest = 0
        output_array.append(bit_cluster)

        return output_array

    def isThereAnyClusterWithErroMoreThan40Percent(self,uartBitClusterArray, frameBeginIdx, currentClusterIdx):
        for i in range(frameBeginIdx, currentClusterIdx + 1):
            bitCluster = uartBitClusterArray[i]
            if (bitCluster.rest >= 0.4):
                return True

        return False

    # This function is called when the uart frame has length bigger than 10 bits
    def tryFixUartFrame(self,uartBitClusterArray, frameBeginIdx, currentClusterIdx):
        byte = ""

        try:
            nextCluster = uartBitClusterArray[currentClusterIdx + 1]
            currentCluster = uartBitClusterArray[currentClusterIdx]

            if currentCluster.value == 1 and nextCluster.value == 0:
                # A stop and starg bit pattern was found. As length is bigger than 9, one single bit should be removed
                for i in range(frameBeginIdx, currentClusterIdx + 1):
                    bitCluster = uartBitClusterArray[i]
                    if (bitCluster.rest >= 0.4):
                        byte += str(bitCluster.value) * (bitCluster.length - 1)
                    else:
                        byte += str(bitCluster.value) * (bitCluster.length)
                return byte[1:-1]  # Return removing Stop Bit (last bit=1)
            else:
                # Next cluster isn't a start bit
                return None

        except Exception as e:
            print(f"Index out of range: {e}")
            return None

    # As Uart transmission starts with most significant bit en finishes with less significant bit, the bit stream readed must be reverted
    def reverseBitOrder(self,bitString):
        return bitString[::-1]
    # ... (outras funções também podem ser adicionadas aqui)

    def gray_to_binary(self,gray):
        binary = ""
        binary += gray[0]  # O bit mais significativo é o mesmo

        for i in range(1, len(gray)):
            # Faz XOR bit a bit do bit atual com o bit mais significativo do número binário até agora
            binary += str(int(gray[i]) ^ int(binary[i - 1]))

        return int(binary, 2)  # Converte a string binária para um número decimal

    def uartDecode(self,uartBitClusterArray):
        ByteStruct = type("ByteStruct", (),
                          {"value": None, "binaryStr": None, "beginSample": None, "beginCluster": None,
                           "endSample": None})

        outputBytes = []
        startBitDetected = False
        byte = ""
        beginSample = 0
        frameBeginIdx = 0
        i = 0

        while i < len(uartBitClusterArray):
            bitCluster = uartBitClusterArray[i]
            bit = bitCluster.value
            if not startBitDetected:
                if bit == 0:
                    startBitDetected = True
                    beginSample = bitCluster.beginSample
                    frameBeginIdx = i
                    if bitCluster.length == 1:
                        byte = ""
                    else:
                        byte = str(bit) * (bitCluster.length - 1)
            elif startBitDetected:
                byte += str(bit) * bitCluster.length
                if len(byte) > 9:
                    # Frame is bad formed
                    if self.isThereAnyClusterWithErroMoreThan40Percent(uartBitClusterArray, frameBeginIdx, i):
                        # One bit cluster must have his length wrong
                        newByte = self.tryFixUartFrame(uartBitClusterArray, frameBeginIdx, i)
                        if newByte != None:
                            startBitDetected = False
                            byteObj = ByteStruct()
                            print(f"Fixed:  {newByte}.  Begin cluster:  {frameBeginIdx}")
                            byteObj.binaryStr = self.reverseBitOrder(newByte)

                            decoded_gray = self.gray_to_binary(byteObj.binaryStr)
                            byteObj.value = decoded_gray

                            # byteObj.value = int(byteObj.binaryStr, 2)
                            byteObj.beginSample = beginSample
                            byteObj.beginCluster = frameBeginIdx
                            outputBytes.append(byteObj)
                            byte = ""
                        else:
                            # Not possible to fix the frame
                            # Restart the frame reading from the initial frame +1. It means 7 frames behind
                            startBitDetected = False
                            i = frameBeginIdx + 1
                    else:
                        # All lengths are well understanded so the frame reading must start at the wrong place
                        startBitDetected = False
                        print("Bad frame detected at cluster: ", i)
                        i = frameBeginIdx + 1  # Restart the frame reading from the initial frame +1. It means 7 frames behind
                elif len(byte) == 9 and bit == 1:
                    # Frame is complete
                    startBitDetected = False
                    byteObj = ByteStruct()
                    byteObj.binaryStr = self.reverseBitOrder(byte[:-1])

                    decoded_gray = self.gray_to_binary(byteObj.binaryStr)
                    byteObj.value = decoded_gray

                    # byteObj.value = int(byteObj.binaryStr, 2)
                    byteObj.beginSample = beginSample
                    byteObj.beginCluster = frameBeginIdx
                    byteObj.endSample = bitCluster.beginSample + bitCluster.length - 1  # Aqui é onde atualizamos endSample

                    outputBytes.append(byteObj)
                    byte = ""
            i = i + 1

        return outputBytes

    def print_bit_cluster_array(self,array):
        for index, bit_cluster in enumerate(array):
            print("{",
                  f"{index}, value={bit_cluster.value}, length={bit_cluster.length}, samplesQtd={bit_cluster.samplesQtd}, rest={bit_cluster.rest}",
                  "}")

    def printByteObjArray(self,byteObjArray):
        for byte in byteObjArray:
            print("{",
                  f"value={byte.value}, chr={chr(byte.value)}, binaryStr={byte.binaryStr}, beginSample={byte.beginSample}, endSample={byte.endSample}, beginCluster={byte.beginCluster}",
                  "}")


    def decode(self,channelNumber=1):

        channelRawValues = self.right_channel if channelNumber == 1 else self.left_channel;

        channelRawValues = np.array(channelRawValues) * -1  # Hardware reception is inverted, this fix this behavior

        binary_data = self.binarize(channelRawValues)  # Exemplo de limiar

        window_start, window_end = self.findTransmitionWindow(binary_data)

        # print("window_start:", window_start)
        # print("window_end:", window_end)

        binary_data = self.autoThresholdBinarization(channelRawValues[window_start: window_end])
        # print("binary_data:", channelRawValues[window_start: window_end])

        zero_min_length, one_min_length = self.calcBitAverageLength(binary_data, 0, window_end - window_start - 1)

        # print("Bit Length:", zero_min_length, one_min_length)

        uartBitClusterArray = self.generateUartBitStream(binary_data, zero_min_length, one_min_length, 0)
        # print("Uart Bit Cluster:")
        # print_bit_cluster_array(uartBitClusterArray)

        decoded_data = self.uartDecode(uartBitClusterArray)

        # ... (outras etapas da decodificação)
        return decoded_data



##------------------------------------------------


# Criar uma instância da classe UartDecoder
decoder = UartDecoder('./test.wav')
utils = TVCUtils()
confidence = 99
min_percent_over_threshold = 17
peaks = utils.find_peaks(decoder.left_channel,confidence,min_percent_over_threshold)
#print("peaks:",peaks)
# Decodificar os dados
decoded_data = decoder.decode(1)
selectedBytes = utils.find_intersection(peaks, decoded_data)
# utils.printByteObjArray(selectedBytes)
num_elements = len(selectedBytes)
print(f"Foram selecionados {num_elements} bytes da sequencia de Gray, considerando a confiança de {confidence}% e um valor de pico acima de {min_percent_over_threshold}% do limiar (max e min)")
print("Mensagem (bynary):", utils.extractBinarySequence(selectedBytes))
print("Mensagem (char - Seq Gray):", utils.extractChrSequence(selectedBytes))
print("Mensagem (char - Bin to Char):", utils.extractChar2Sequence(selectedBytes))
print("Mensagem (char - Portuguese Chars):", utils.extractPortugueseSequence(selectedBytes))


