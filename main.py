from UartDecoder import UartDecoder
from PeakFinder import PeakFinder

# audioPath = 'C:/Users/DTI Digital/Desktop/test/test-exp1.wav'
audioPath = '/workspaces/uartDecoder/test-exp1.wav'


decoder = UartDecoder(audioPath)
print("Analisando o arquivo ", audioPath)
utils = PeakFinder()

def printDecodedResult(result):
    print("Peak Idx: ", result.peak.peakIdx) 
    decoder.printByteStructArray(result.selectedBytes)
    print("\n")

def decodeDataAroundPeaks(peaks, samplesQtdBeforePeak = 24000, samplesQtdAfterPeak = 500):
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
        decodedArray = decoder.decodeDataSlice(sliceBegin, sliceEnd)
        print("Decoded Array:")
        decoder.printByteStructArray(decodedArray)
        
        dataSampleOffset = sliceBegin
        peakAndData.selectedBytes = utils.find_intersection([peak], decodedArray, dataSampleOffset) 
        peakAndData.elementsQtd = len(peakAndData.selectedBytes)
        # pickAndData.header = uartDataPackage.getMessageHeader(byteArray)
        peakAndData.peak = peak
        peakAndData.peakIdx = i  
        results.append(peakAndData)
        totalBytesSelected += peakAndData.elementsQtd
        if i == 1:
            break                       

    return results, totalBytesSelected

# TODO
# For C:/Users/DTI Digital/Desktop/test/test-exp1.wav, two peaks have the position at 19.83s
# For C:/Users/DTI Digital/Desktop/test/test-exp1.wav, peaks at 47.4130 and 2:427090 weren't find
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
    for i, result in enumerate(results):
        printDecodedResult(result)
       

    # print(f"Iteração {iteracao}: foram selecionados {totalBytesSelected} bytes da sequencia de Gray, considerando a confiança de {confidence}% e um valor de pico acima de {min_percent_over_threshold}% do limiar (max e min), com um fator de filtro de {filterFactor}")
    # utils.printtable(result.selectedBytes)
    # print('BIN:',utils.extractBinarySequence(result.selectedBytes))
    # print('CHAR(Gray):',utils.extractChrSequence(result.selectedBytes))
    # print('CHAR(BIN):',utils.extractChar2Sequence(result.selectedBytes))
    # print('CHAR(PT-BR):',utils.extractPortugueseSequence(result.selectedBytes))



