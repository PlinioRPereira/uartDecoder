from UartDecoder import UartDecoder
from PeakFinder import PeakFinder

audioPath = 'C:/Users/DTI Digital/Desktop/test/test-exp1.wav'

decoder = UartDecoder(audioPath)
print("Analisando o arquivo ", audioPath)
utils = PeakFinder()

def decodeDataAroundPeaks(peaks, signalLength, samplesQtdBeforePeak = 1000, samplesQtdAfterPeak = 50):
    PickAndDataStruct = type("PickAndDataStruct", (),
        {"selectedBytes": None, "elementsQtd": None, "header": None, "peak": None })
    result = []
    totalBytesSelected = 0
    
    for i, peak in enumerate(peaks):
        pickAndData = PickAndDataStruct()        
        sliceBegin = peak.peak_start - samplesQtdBeforePeak if peak.peak_start > samplesQtdBeforePeak else 0
        sliceEnd = peak.peak_end + samplesQtdAfterPeak if peak.peak_end + samplesQtdAfterPeak < signalLength else signalLength-1  
        byteArray = decoder.decodeDataSlice(sliceBegin, sliceEnd)
        pickAndData.selectedBytes = utils.find_intersection(list(peak), byteArray)
        pickAndData.elementsQtd = len(pickAndData.selectedBytes)
        # pickAndData.header = uartDataPackage.getMessageHeader(byteArray)
        pickAndData.peak = peak        
        result.append(pickAndData)
        totalBytesSelected += pickAndData.elementsQtd
        print(byteArray)        

    return result, totalBytesSelected

# TODO
# For C:/Users/DTI Digital/Desktop/test/test-exp1.wav, two peaks have the position at 19.83s
# For C:/Users/DTI Digital/Desktop/test/test-exp1.wav, peaks at 47.4130 and 2:427090 weren't find
for iteracao in range(1, 2):
    confidence = 96-iteracao
    min_percent_over_threshold = 45
    filterFactor = 0.75
    
    allPeaks = utils.find_peaks(decoder.left_channel, confidence, min_percent_over_threshold)

    # peaks = utils.filter_peaks(allPeaks, filterFactor)

    print("----------------------------------------------------------------------------")
    print("ITERAÇAO ", iteracao)
    print("Total de Picos:", len(allPeaks) )
    # print(allPeaks) 
    utils.printPeaks(allPeaks) 
    print("\n")
    
    # formatedPeaks = utils.format_peaks(peaks)
    # print("Lista de Picos:",formatedPeaks)
    # Decodificar os dados

    # result, totalBytesSelected = decodeDataAroundPeaks(peaks)

    # print(f"Iteração {iteracao}: foram selecionados {totalBytesSelected} bytes da sequencia de Gray, considerando a confiança de {confidence}% e um valor de pico acima de {min_percent_over_threshold}% do limiar (max e min), com um fator de filtro de {filterFactor}")
    # utils.printtable(result.selectedBytes)
    # print('BIN:',utils.extractBinarySequence(result.selectedBytes))
    # print('CHAR(Gray):',utils.extractChrSequence(result.selectedBytes))
    # print('CHAR(BIN):',utils.extractChar2Sequence(result.selectedBytes))
    # print('CHAR(PT-BR):',utils.extractPortugueseSequence(result.selectedBytes))



