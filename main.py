from UartDecoder import UartDecoder
from PeakFinder import PeakFinder
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from scipy.signal import hilbert
from scipy.signal import butter, lfilter
from AudioSensor import AudioSensor
import threading

utils = PeakFinder()

def printDecodedResult(result):
    print("Peak Idx: ", result.peakIdx) 
    for selectedByte in result.selectedBytes:
        decoder.printByteStructArray([selectedByte])

def decodeDataAroundPeaks(peaks, samplesQtdBeforePeak = 24000, samplesQtdAfterPeak = 500, usingParity=True):
    PeakAndDataStruct = type("PeakAndDataStruct", (),
        {"selectedBytes": None, "elementsQtd": None, "header": None, "peak": None, "peakIdx": None })
    results = []
    totalBytesSelected = 0

    for i, peak in enumerate(peaks):
        print("\nProcessing peak: ", i)
        peakAndData = PeakAndDataStruct()        
        sliceBegin = peak.start - samplesQtdBeforePeak if peak.start > samplesQtdBeforePeak else 0
        sliceEnd = peak.end + samplesQtdAfterPeak if peak.end + samplesQtdAfterPeak < decoder.signalLength else decoder.signalLength-1  
        print("SliceBegin: ", sliceBegin)        
        print("BeginTime: ", utils.get_peak_time(sliceBegin, 44100))
        print("EndTime: ", utils.get_peak_time(sliceEnd, 44100))
        
        print("Decoding Slice...")   
        decodedArray = decoder.decodeDataSlice(sliceBegin, sliceEnd, usingParity=False)
        # print("Decoded Array:")
        # decoder.printByteStructArray(decodedArray)
        
        dataSampleOffset = sliceBegin
        peakAndData.selectedBytes = utils.find_intersection([peak], decodedArray, dataSampleOffset) 
        peakAndData.elementsQtd = len(peakAndData.selectedBytes)
        # pickAndData.header = uartDataPackage.getMessageHeader(byteArray)
        peakAndData.peak = peak
        peakAndData.peakIdx = i  
        results.append(peakAndData)
        totalBytesSelected += peakAndData.elementsQtd
        
    return results, totalBytesSelected


def plot_combined_graph_corrected(x, y, peaks_indices, window=20, filename='teste.png'):
    num_peaks = len(peaks_indices)
    if num_peaks == 0:
        return

    # Configuração do layout da grade
    cols = 4  # Agora temos 4 colunas: 2 para cada pico
    rows = num_peaks + 1  # Uma linha para o gráfico principal e uma para cada pico

    fig = plt.figure(figsize=(12, 3 * rows))
    gs = GridSpec(rows, cols, figure=fig)

    # Plot do gráfico principal
    ax_main = fig.add_subplot(gs[0, :2])
    ax_main.plot(x, y, label='Série de Dados')
    ax_main.scatter(x[peaks_indices], y[peaks_indices], color='red', label='Picos')
    ax_main.legend()
    ax_main.set_title('Gráfico Principal')
    ax_main.set_xlabel('Eixo samplesLimit')
    ax_main.set_ylabel('Eixo Y')

    # Plot dos gráficos de pico
    for i, peak_idx in enumerate(peaks_indices):
        # Gráfico com janela ampliada (o dobro da original)
        ax1 = fig.add_subplot(gs[i + 1, :2])

        start = max(0, peak_idx - 2 * window)
        end = min(len(x), peak_idx + 2 * window)

        ax1.plot(x[start:end], y[start:end], label='Entorno do Pico')
        ax1.scatter(x[peak_idx], y[peak_idx], color='red', label='Pico')
        ax1.legend()
        ax1.set_title(f'Pico {i + 1} - Janela Ampliada')
        ax1.set_xlabel('Eixo samplesLimit')
        ax1.set_ylabel('Eixo Y')

        # Gráfico com janela original
        ax2 = fig.add_subplot(gs[i + 1, 2:])

        start = max(0, peak_idx - window)
        end = min(len(x), peak_idx + window)

        ax2.plot(x[start:end], y[start:end], label='Entorno do Pico')
        ax2.scatter(x[peak_idx], y[peak_idx], color='red', label='Pico')
        ax2.legend()
        ax2.set_title(f'Pico {i + 1} - Janela Original')
        ax2.set_xlabel('Eixo samplesLimit')
        ax2.set_ylabel('Eixo Y')

    plt.tight_layout()
    plt.savefig(filename)
    plt.show()


def plot_and_save_graph(points: np.ndarray, indexes: np.ndarray, filename: str, window=20):
    # Gera o gráfico combinado
    plot_combined_graph_corrected(np.arange(len(points)), points, indexes, window,filename)


def transform_peaks_to_indexes(peaks):
    return [peak.position for peak in peaks]

def getFilteredSignal(signal,frequencia_de_corte = 8000,fs=10000*2):
    # Configuração do filtro passa-baixa
    # Frequência de corte em Hz
    ordem_do_filtro = 8  # Ordem do filtro

    # Calcula os coeficientes do filtro passa-baixa Butterworth
    b, a = butter(ordem_do_filtro, frequencia_de_corte, fs=fs, btype='low')

    # Aplica o filtro passa-baixa ao sinal
    sinal_filtrado = lfilter(b, a, signal)

    return sinal_filtrado


def getEnvelop(signal):
    return np.abs(hilbert(signal))


def handleAnalyseAudio(signal, confidence = 95, min_percent_over_threshold = 30, filterFactor=80):

    allPeaks = utils.find_peaks(signal, confidence, min_percent_over_threshold)

    # peaks = utils.filter_peaks(allPeaks, filterFactor/100)
    peaks = utils.simple_filter_peaks(allPeaks, filterFactor)
    # peaks = allPeaks

    if len(peaks)>0:
        print("Total de Picos:", len(peaks))
        utils.printPeaks(peaks)
        print("\n")
        # formatedPeaks = utils.format_peaks(peaks)

        # Decode data
        results, totalBytesSelected = decodeDataAroundPeaks(peaks, usingParity=False)
        print("----------------------------------------------------------------------------")
        print("DECODIFICAÇÃO")
        utils.printtable(results)
        print('BIN:', utils.extractBinarySequence(results))
        print('CHAR(Gray):', utils.extractChrSequence(results))
        print('CHAR(BIN):', utils.extractChar2Sequence(results))
        print('CHAR(PT-BR):', utils.extractPortugueseSequence(results))
        print('Raw data: ')
        for result in results:
            printDecodedResult(result)


        # plot_and_save_graph(signal, transform_peaks_to_indexes(peaks), f'Iteracao-{iteracao}.png')
        
    
dataA = []
dataB = []
samplesLimit = 48000
dataSampleA=[]
dataSampleB=[]
decoder=False
isRun=True


loadFromFile = True

if loadFromFile:
    audioPath = 'C:/Users/DTI Digital/Desktop/test/test-exp1.wav'
    # audioPath = 'test-exp1.wav'
    audioPath = 'C:/Users/DTI Digital/Documents/TVC/TVC_Data.wav'
    print("Analisando o arquivo ", audioPath)
    decoder = UartDecoder(audioPath)
    signal = getFilteredSignal(decoder.left_channel)  # Filter
    signal = decoder.left_channel
    handleAnalyseAudio(decoder.left_channel)

    # TEST
    # decodedArray = decoder.decodeDataSlice(0, 100000)
    # decoder.printByteStructArray(decodedArray)


else:
    audioSensor = AudioSensor()
    audioSensor.list_audio_devices()
    timeout = 60  # 5x60s = 5min


    def onStart(serialInstance):
        global isRun
        isRun = True
        print(f'Iniciando o contato - Tempo de contato: {timeout} seguundos')


    def onStop(data, sensorData):
        global isRun
        isRun = False
        print(f'Finalizando o contato')


    def onData(channelA, channelB):
        global dataA, dataB, dataSampleA, dataSampleB, decoder

        # Acrescentando novos dados
        dataA.extend(channelA)
        dataB.extend(channelB)

        while len(dataB) >= samplesLimit:
            # Extração das amostras iniciais
            dataSampleB = dataB[:samplesLimit]

            # Remoção das amostras utilizadas
            dataB = dataB[samplesLimit:]

        while len(dataA) >= samplesLimit:
            # Extração das amostras iniciais
            dataSampleA = dataA[:samplesLimit]

            # Remoção das amostras utilizadas
            dataA = dataA[samplesLimit:]

            decoder = UartDecoder(False, dataSampleA, dataSampleB)

            handleAnalyseAudio(dataSampleA)



    def sensor_task():
        audioSensor.startSensor(onStart, onData, onStop, timeout)
        print("Sensor iniciado")


    thread1 = threading.Thread(target=sensor_task)
    thread1.start()
    thread1.join()


