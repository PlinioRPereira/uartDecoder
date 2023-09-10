import wave
import numpy as np
import matplotlib.pyplot as plt

def open_uart_wav(file_path):
    wav = wave.open(file_path, 'rb')

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

    return left_channel, right_channel

def binarize(channelData, threshold):
    binary_array = [1 if sample > threshold else 0 for sample in channelData]
    return binary_array

# windowSize Amont of samples to calc the threshold
def autoThresholdBinarization(samples, windowSize):
    binary_array = []
    
    for i in range(0, len(samples), windowSize):
        window = samples[i:i+windowSize]
        threshold = (max(window) + min(window)) / 2
        
        binarized_window = [1 if sample >= threshold else 0 for sample in window]
        binary_array.extend(binarized_window)
    
    return binary_array

def findTransmitionWindow(binary_array, raiseAndFallEdgesQtd):
    window_start = None
    window_end = None
    transitions = 0
    startPrefixSamplesQtd = 50            # Add 50 samples before window_start to facilitate decoding

    for i in range(len(binary_array) - 1):
        if binary_array[i] != binary_array[i + 1]:
            transitions += 1

            if transitions == 1:
                window_start = i

            if transitions == raiseAndFallEdgesQtd:
                window_end = i
                break
    
    if(window_start > startPrefixSamplesQtd):
        window_start = window_start - startPrefixSamplesQtd

    return window_start, window_end

def calculate_average_length(array, x):
    total = 0
    count = 0
    
    for num in array:
        if num in (x-1, x, x+1):
            total += num
            count += 1
    
    if count > 0:
        average = total / count
        return average
    else:
        return None

def calcBitAverageLength(binary_array, window_start, window_end):
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

    zero_min_length = calculate_average_length(zeros_lengths, min(zeros_lengths) if zeros_lengths else 0)
    one_min_length = calculate_average_length(ones_lengths, min(ones_lengths) if ones_lengths else 0)

    return zero_min_length, one_min_length

def generateUartBitStream(binary_array, zeroBitLength, oneBitLength, beginSampleOffest):
    BitCluster = type("BitCluster", (), {"value": None, "length": None, "samplesQtd": None, "rest": None, "beginSample": None })
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

def isThereAnyClusterWithErroMoreThan40Percent(uartBitClusterArray, frameBeginIdx, currentClusterIdx):
    for i in range(frameBeginIdx, currentClusterIdx+1):
        bitCluster = uartBitClusterArray[i]               
        if (bitCluster.rest >= 0.4): 
            return True
    
    return False

# This function is called when the uart frame has length bigger than 10 bits
def tryFixUartFrame(uartBitClusterArray, frameBeginIdx, currentClusterIdx):
    byte = ""
    
    try:
        nextCluster = uartBitClusterArray[currentClusterIdx+1]
        currentCluster = uartBitClusterArray[currentClusterIdx]
        
        if currentCluster.value == 1 and nextCluster.value == 0: 
            # A stop and starg bit pattern was found. As length is bigger than 9, one single bit should be removed
            for i in range(frameBeginIdx, currentClusterIdx+1):
                bitCluster = uartBitClusterArray[i] 
                if(bitCluster.rest >= 0.4):
                    byte += str(bitCluster.value) * (bitCluster.length-1)
                else:
                    byte += str(bitCluster.value) * (bitCluster.length)
            return byte[1:-1]   # Return removing Stop Bit (last bit=1)
        else:
            # Next cluster isn't a start bit
            return None
    
    except Exception as e: 
        print(f"Index out of range: {e}")
        return None

#As Uart transmission starts with most significant bit en finishes with less significant bit, the bit stream readed must be reverted
def reverseBitOrder(bitString):
    return bitString[::-1]

#Receives an stream of 0s and 1s bits and return an array of numbers decoded 
def uartDecode(uartBitClusterArray):
    ByteStruct = type("ByteStruct", (), {"value": None, "binaryStr": None, "beginSample": None, "beginCluster": None })
    outputBytes = []
    startBitDetected = False
    byte = ""
    beginSample = 0
    frameBeginIdx = 0
    i=0

    while i < len(uartBitClusterArray) :
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
                if isThereAnyClusterWithErroMoreThan40Percent(uartBitClusterArray, frameBeginIdx, i):               
                    # One bit cluster must have his length wrong
                    newByte = tryFixUartFrame(uartBitClusterArray, frameBeginIdx, i)
                    if newByte != None:                        
                        startBitDetected = False            
                        byteObj = ByteStruct()
                        print(f"Fixed:  {newByte}.  Begin cluster:  {frameBeginIdx}")                                        
                        byteObj.binaryStr = reverseBitOrder(newByte)  
                        byteObj.value = int(byteObj.binaryStr, 2)                 
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
                    print("Bad frame detected at cluster: ",  i)
                    i = frameBeginIdx + 1           # Restart the frame reading from the initial frame +1. It means 7 frames behind
            elif len(byte) == 9 and bit == 1:
                # Frame is complete
                startBitDetected = False            
                byteObj = ByteStruct()
                byteObj.binaryStr = reverseBitOrder(byte[:-1])  
                byteObj.value = int(byteObj.binaryStr, 2)                 
                byteObj.beginSample = beginSample
                byteObj.beginCluster = frameBeginIdx  
                outputBytes.append(byteObj)
                # print(f"Readed:    {byte[:-1]}.    Begin cluster:  {frameBeginIdx}" )                
                byte = ""
        i = i + 1           

    return outputBytes

def print_bit_cluster_array(array):
    for index, bit_cluster in enumerate(array):
        print("{", f"{index}, value={bit_cluster.value}, length={bit_cluster.length}, samplesQtd={bit_cluster.samplesQtd}, rest={bit_cluster.rest}", "}")

def printByteObjArray(byteObjArray):
    for byte in byteObjArray:
        print("{", f"value={byte.value}, chr={chr(byte.value)}, binaryStr={byte.binaryStr}, beginSample={byte.beginSample}, beginCluster={byte.beginCluster}", "}")

########################################################################################
# # Test uart_decode
# binary_array_test = [1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1]  # Your binary array
# decoded_data = uart_decode(binary_array_test)
# decoded_decimal = ", ".join(str(byte) for byte in decoded_data)
# decoded_hex = ", ".join(format(byte, '02X') for byte in decoded_data)

# print("Decoded Data (Decimal):", decoded_decimal)
# print("Decoded Data (Hexadecimal):", decoded_hex)

###########################################################################################
# Exemplo de uso
# Decodifica Uart no padrão start bit, 8 bits de dados, stop bit

threshold = 0
samplesQtdToCalcThreshold = 100
raiseAndFallEdgesQtd = 20000
# rawLeftChannel, rawRightChannel = open_uart_wav('C:/Users/DTI Digital/Desktop/exp5.wav')
rawLeftChannel, rawRightChannel = open_uart_wav('C:/Users/DTI Digital/Desktop/grayBackwords.wav')

rightChannel = np.array(rawRightChannel) * -1       # Hardware reception is inverted, this fix this behavior 

binaryRightChannel = binarize(rightChannel, threshold)
window_start, window_end = findTransmitionWindow(binaryRightChannel, raiseAndFallEdgesQtd)
binaryRightChannel = autoThresholdBinarization(rightChannel[window_start : window_end], samplesQtdToCalcThreshold)
print("Left Channel:", window_start)
print("Right Channel:", window_end)

zero_min_length, one_min_length = calcBitAverageLength(binaryRightChannel, 0,  window_end - window_start-1)
print("Bit Length:", zero_min_length, one_min_length)

uartBitClusterArray = generateUartBitStream(binaryRightChannel, zero_min_length, one_min_length, 0)
# print("Uart Bit Cluster:")
# print_bit_cluster_array(uartBitClusterArray)

outputBytes = uartDecode(uartBitClusterArray)
print("Bytes Decoded:")
printByteObjArray(outputBytes)

# newVetor = np.array(binaryRightChannel) * 2000
# plt.plot(rightChannel[window_start : window_end], label='Audio')
# plt.plot(newVetor, label='Binarization')
# plt.show()

# Imprime os arrays de cada canal
# print("Left Channel:", binaryRightChannel[:100000])
# print("Canal Direito:", right_channel)


