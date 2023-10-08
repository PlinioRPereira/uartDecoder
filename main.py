from UartDecoder import UartDecoder
from PeakFinder import PeakFinder

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

    # for i, result in enumerate(results):
    #     printDecodedResult(result)


