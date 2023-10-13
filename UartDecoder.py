import wave
import numpy as np
import time

class UartDecoder:
    def __init__(self, file_path, threshold=0, samplesQtdToCalcThreshold=100, raiseAndFallEdgesQtd=20):
        self.file_path = file_path
        self.left_channel, self.right_channel = self.open_uart_wav()  # Removido o argumento adicional
        self.threshold = threshold
        self.samplesQtdToCalcThreshold = samplesQtdToCalcThreshold
        self.raiseAndFallEdgesQtd = raiseAndFallEdgesQtd
        self.signalLength = len(self.left_channel) 

        self.BitCluster = type("BitCluster", (),
                            {"value": None, "length": None, "samplesQtd": None, "rest": None, "beginSample": None})
        
        self.ByteStruct = type("ByteStruct", (),
                            {"value": None, "binaryStr": None, "beginSample": None, "beginCluster": None,
                            "endSample": None})      

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

    def autoThresholdBinarization(self, samples):
        binary_array = []
        samplesQtd = len(samples)
        windowSize = self.samplesQtdToCalcThreshold 

        for i in range(0, samplesQtd, windowSize):
            if(i+windowSize > samplesQtd):
                window = samples[i:samplesQtd]
            else:   
                window = samples[i:i + windowSize]            
            threshold = (max(window) + min(window)) / 2

            binarized_window = [1 if sample >= threshold else 0 for sample in window]
            binary_array.extend(binarized_window)

        return binary_array

    def findTransmitionWindow(self, binaryArray, raiseAndFallEdgesQtd):
        window_start = None
        window_end = None
        transitions = 0
        startPrefixSamplesQtd = 50      # Set start to 50 samples before window_start to facilitate decoding

        for i in range(len(binaryArray) - 1):
            if binaryArray[i] != binaryArray[i + 1]:
                transitions += 1

                if transitions == 1:
                    window_start = i

                if transitions == raiseAndFallEdgesQtd:
                    window_end = i
                    break
        
        if window_start > startPrefixSamplesQtd:
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

    def calcBitAverageLength(self, binary_array, window_start, window_end):
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

    def generateUartBitStream(self, binary_array, zeroBitLength, oneBitLength, beginSampleOffest=0):
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
                bit_cluster = self.BitCluster()
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

        bit_cluster = self.BitCluster()
        bit_cluster.value = current_value
        bit_cluster.length = round(current_length / bitLength)
        bit_cluster.samplesQtd = current_length
        bit_cluster.rest = 0
        bit_cluster.beginSample = beginSample
        output_array.append(bit_cluster)

        return output_array

    def isThereAnyClusterWithErroMoreThan40Percent(self, uartBitClusterArray, frameBeginIdx, currentClusterIdx):
        for i in range(frameBeginIdx, currentClusterIdx + 1):
            bitCluster = uartBitClusterArray[i]
            if (bitCluster.rest >= 0.4):
                return True

        return False

    # This function is called when the uart frame has length bigger than 10 bits
    def tryFixUartFrame(self, uartBitClusterArray, frameBeginIdx, currentClusterIdx):
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
                if(len(byte) == 10):                                                 # 1 Start + 8 data bits + stop
                    return byte[1:-1]  # Return removing Stop Bit (last bit=1)
                else:
                    return None
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

    def grayToBinary(self, gray):
        binary = ""
        binary += gray[0]  # O bit mais significativo é o mesmo

        for i in range(1, len(gray)):
            # Faz XOR bit a bit do bit atual com o bit mais significativo do número binário até agora
            binary += str(int(gray[i]) ^ int(binary[i - 1]))

        return int(binary, 2)  # Converte a string binária para um número decimal

    def uartDecode(self, uartBitClusterArray):
        outputBytes = []
        startBitDetected = False
        byte = ""
        beginSample = 0
        frameBeginClusterIdx = 0
        i = 0

        while i < len(uartBitClusterArray):
            bitCluster = uartBitClusterArray[i]
            bit = bitCluster.value
            if not startBitDetected:
                if bit == 0:
                    startBitDetected = True
                    beginSample = bitCluster.beginSample
                    frameBeginClusterIdx = i
                    if bitCluster.length == 1:
                        byte = ""
                    else:
                        byte = str(bit) * (bitCluster.length - 1)
            elif startBitDetected:
                byte += str(bit) * bitCluster.length
                if len(byte) > 9:
                    # Frame is bad formed
                    if self.isThereAnyClusterWithErroMoreThan40Percent(uartBitClusterArray, frameBeginClusterIdx, i):
                        # One bit cluster must have his length wrong
                        newByte = self.tryFixUartFrame(uartBitClusterArray, frameBeginClusterIdx, i)
                        if newByte != None:
                            startBitDetected = False
                            byteObj = self.ByteStruct()
                            print(f"Fixed:  {newByte}.  Begin cluster:  {frameBeginClusterIdx}")
                            byteObj.binaryStr = self.reverseBitOrder(newByte)

                            decoded_gray = self.grayToBinary(byteObj.binaryStr)
                            byteObj.value = decoded_gray                            
                            byteObj.beginCluster = frameBeginClusterIdx
                            byteObj.beginSample = beginSample
                            byteObj.endSample = bitCluster.beginSample + bitCluster.samplesQtd - 1
                            outputBytes.append(byteObj)
                            byte = ""
                        else:
                            # Not possible to fix the frame
                            # Restart the frame reading from the initial frame +1. It means 7 frames behind
                            startBitDetected = False
                            i = frameBeginClusterIdx + 1
                    else:
                        # All lengths are well understanded so the frame reading must start at the wrong place
                        startBitDetected = False
                        print("Bad frame detected at cluster: ", i)
                        i = frameBeginClusterIdx + 1  # Restart the frame reading from the initial frame +1. It means 7 frames behind
                elif len(byte) == 9 and bit == 1:
                    # This bit is stop bit. Frame is complete
                    startBitDetected = False
                    
                    byteObj = self.ByteStruct()
                    byteObj.binaryStr = self.reverseBitOrder(byte[:-1])
                    decoded_gray = self.grayToBinary(byteObj.binaryStr)
                    byteObj.value = decoded_gray
                    # byteObj.value = int(byteObj.binaryStr, 2)                    
                    byteObj.beginSample = beginSample                    
                    byteObj.beginCluster = frameBeginClusterIdx
                    byteObj.endSample = bitCluster.beginSample + bitCluster.samplesQtd - 1
                    outputBytes.append(byteObj)                    
                    byte = ""
            i = i + 1

        return outputBytes

    def printBitClusterArray(self, array):
        print("{:<6} {:<6} {:<6} {:<6} {:<12} {:<10}".format('index', 'value', 'length', 'samplesQtd', 'rest', 'beginSample'))        
        for index, bit_cluster in enumerate(array):
            print("{:<6} {:<6} {:<6} {:<6} {:<12} {:<10}".format(
                index, 
                bit_cluster.value,
                bit_cluster.length,
                bit_cluster.samplesQtd,
                round(bit_cluster.rest, 6),
                bit_cluster.beginSample
            ))

    def printByteStructArray(self, byteObjArray):
        for byte in byteObjArray:
            print("{",
                    f"value={byte.value}, chr={chr(byte.value)}, binaryStr={byte.binaryStr}, beginSample={byte.beginSample}, endSample={byte.endSample}, beginCluster={byte.beginCluster}",
                    "}")

    def preprocessSignalData(self, channelNumber=1, sliceBegin=0, sliceEnd=100, invertSignal=True):
        
        if channelNumber == 1:
            channelRawValues = self.right_channel[sliceBegin:sliceEnd]
        else:
            channelRawValues = self.left_channel[sliceBegin:sliceEnd]

        channelRawValues = np.array(channelRawValues) * -1 if invertSignal else np.array(channelRawValues)       # Hardware reception is inverted, this fix this behavior

        self.binaryData = self.binarize(channelRawValues)

        windowStart, windowEnd = self.findTransmitionWindow(self.binaryData, self.raiseAndFallEdgesQtd)
        # print("window_start:", windowStart)
        # print("window_end:", windowEnd)

        binaryData = self.autoThresholdBinarization(channelRawValues[windowStart: sliceEnd])        

        return binaryData, windowStart, windowEnd

    def decode(self, channelNumber=1, invertSignal=True):

        channelRawValues = self.right_channel if channelNumber == 1 else self.left_channel

        channelRawValues = np.array(channelRawValues) * -1 if invertSignal else np.array(channelRawValues)         # Hardware reception is inverted, this fix this behavior

        binary_data = self.binarize(channelRawValues)  # Exemplo de limiar

        window_start, window_end = self.findTransmitionWindow(binary_data)

        print("window_start:", window_start)
        print("window_end:", window_end)

        binary_data = self.autoThresholdBinarization(channelRawValues[window_start: window_end])
        # print("binary_data:", channelRawValues[window_start: window_end])

        zero_min_length, one_min_length = self.calcBitAverageLength(binary_data, 0, window_end - window_start - 1)

        # print("Bit Length:", zero_min_length, one_min_length)

        uartBitClusterArray = self.generateUartBitStream(binary_data, zero_min_length, one_min_length, 0)
        # print("Uart Bit Cluster:")
        # printBitClusterArray(uartBitClusterArray)

        decoded_data = self.uartDecode(uartBitClusterArray)

        # ... (outras etapas da decodificação)
        return decoded_data

    # sliceBegin and sliceEnd are the sample position in raw data
    # windowStart and windowEnd are the sample position in raw data
    # binaryData is a new array of the size sliceEnd - windowStart
    def decodeDataSlice(self, sliceBegin=0, sliceEnd=100):

        binaryData, windowStart, windowEnd = self.preprocessSignalData(1, sliceBegin, sliceEnd)
        
        zeroMinLength, oneMinLength = self.calcBitAverageLength(binaryData, 0, windowEnd - windowStart - 1)
        # print("Bit Length:", zeroMinLength, oneMinLength)

        uartBitClusterArray = self.generateUartBitStream(binaryData, zeroMinLength, oneMinLength)
        # print("Uart Bit Cluster:")
        # self.printBitClusterArray(uartBitClusterArray)

        decoded_data = self.uartDecode(uartBitClusterArray)

        return decoded_data

        
