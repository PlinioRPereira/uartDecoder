from UartDecoder import UartDecoder
from PeakFinder import PeakFinder
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec


# audioPath = 'C:/Users/DTI Digital/Desktop/test/test-exp1.wav'
audioPath = 'test-exp1.wav'


decoder = UartDecoder(audioPath)
print("Analisando o arquivo ", audioPath)
utils = PeakFinder()

def printDecodedResult(result):
    print("Peak Idx: ", result.peakIdx) 
    decoder.printByteStructArray(result.selectedBytes)
    print("\n")

def decodeDataAroundPeaks(peaks, samplesQtdBeforePeak = 24000, samplesQtdAfterPeak = 500):
    PeakAndDataStruct = type("PeakAndDataStruct", (),
        {"selectedBytes": None, "elementsQtd": None, "header": None, "peak": None, "peakIdx": None })
    results = []
    totalBytesSelected = 0

    for i, peak in enumerate(peaks):
        # if i != 3: 
        #     continue 
        print("\nProcessing peak: ", i)
        peakAndData = PeakAndDataStruct()        
        sliceBegin = peak.start - samplesQtdBeforePeak if peak.start > samplesQtdBeforePeak else 0
        sliceEnd = peak.end + samplesQtdAfterPeak if peak.end + samplesQtdAfterPeak < decoder.signalLength else decoder.signalLength-1  
        print("SliceBegin: ", sliceBegin)        
        print("BeginTime: ", utils.get_peak_time(sliceBegin, 44100))
        print("EndTime: ", utils.get_peak_time(sliceEnd, 44100))
        
        print("Decoding Slice...")   
        decodedArray = decoder.decodeDataSlice(sliceBegin, sliceEnd)
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
        # if i == 3:
        #     break                       

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
    ax_main.set_xlabel('Eixo X')
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
        ax1.set_xlabel('Eixo X')
        ax1.set_ylabel('Eixo Y')

        # Gráfico com janela original
        ax2 = fig.add_subplot(gs[i + 1, 2:])

        start = max(0, peak_idx - window)
        end = min(len(x), peak_idx + window)

        ax2.plot(x[start:end], y[start:end], label='Entorno do Pico')
        ax2.scatter(x[peak_idx], y[peak_idx], color='red', label='Pico')
        ax2.legend()
        ax2.set_title(f'Pico {i + 1} - Janela Original')
        ax2.set_xlabel('Eixo X')
        ax2.set_ylabel('Eixo Y')

    plt.tight_layout()
    plt.savefig(filename)
    plt.show()


def plot_and_save_graph(points: np.ndarray, indexes: np.ndarray, filename: str, window=20):
    # Gera o gráfico combinado
    plot_combined_graph_corrected(np.arange(len(points)), points, indexes, window,filename)


def transform_peaks_to_indexes(peaks):
    return [peak.position for peak in peaks]



# TODO
# For C:/Users/DTI Digital/Desktop/test/test-exp1.wav, two peaks have the position at 19.83s. Threat this
# For C:/Users/DTI Digital/Desktop/test/test-exp1.wav, peaks at 47.4130 and 2:427090 weren't find
# Check decoded data for all the 5 peaks
# Check what happens when a peak occours in non decoded data
# Improve decode algorithm to don't miss any data
for iteracao in range(1, 2):
    confidence = 96-iteracao
    min_percent_over_threshold = 45
    filterFactor = 0.4
    
    allPeaks = utils.find_peaks(decoder.left_channel, confidence, min_percent_over_threshold)

    peaks = utils.filter_peaks(allPeaks, filterFactor)

    print("----------------------------------------------------------------------------")
    print("ITERAÇAO ", iteracao)
    print("Total de Picos:", len(peaks))
    utils.printPeaks(peaks) 
    print("\n")
    # formatedPeaks = utils.format_peaks(peaks)
    
    # Decode data
    results, totalBytesSelected = decodeDataAroundPeaks(peaks)
    print("----------------------------------------------------------------------------")
    print("DECODIFICAÇÃO")
    utils.printtable(results)
    print('BIN:',utils.extractBinarySequence(results))
    print('CHAR(Gray):',utils.extractChrSequence(results))
    print('CHAR(BIN):',utils.extractChar2Sequence(results))
    print('CHAR(PT-BR):',utils.extractPortugueseSequence(results))

    plot_and_save_graph(decoder.left_channel,transform_peaks_to_indexes(peaks),f'Iteracao-{iteracao}.png')




    # for i, result in enumerate(results):
    #     printDecodedResult(result)


