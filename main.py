from UartDecoder import UartDecoder
from PeakFinder import PeakFinder

audioPath = './test-exp2.wav'

decoder = UartDecoder(audioPath)
print("Anaĺisando o arquivo ",audioPath)
print("Extraindo canais de audio e preparando a sequencia de Gray...")
decoded_data = decoder.decode(1)
print("Preparado!")
utils = PeakFinder()

for iteracao in range(1, 6):
    confidence = 96-iteracao
    min_percent_over_threshold = 45
    filterFactor = 0.75
    allPeaks = utils.find_peaks(decoder.left_channel,confidence,min_percent_over_threshold)

    peaks = utils.filter_peaks(allPeaks,filterFactor)

    print("----------------------------------------------------------------------------")
    print("ITERAÇAO ",iteracao)

    print("Total de Picos:", len(peaks) )
    formatedPeaks = utils.format_peaks(peaks)
    # print("Lista de Picos:",formatedPeaks)
    # Decodificar os dados

    selectedBytes = utils.find_intersection(peaks, decoded_data)
    num_elements = len(selectedBytes)
    print(f"Iteração {iteracao}: foram selecionados {num_elements} bytes da sequencia de Gray, considerando a confiança de {confidence}% e um valor de pico acima de {min_percent_over_threshold}% do limiar (max e min), com um fator de filtro de {filterFactor}")
    utils.printtable(selectedBytes)
    print('BIN:',utils.extractBinarySequence(selectedBytes))
    print('CHAR(Gray):',utils.extractChrSequence(selectedBytes))
    print('CHAR(BIN):',utils.extractChar2Sequence(selectedBytes))
    print('CHAR(PT-BR):',utils.extractPortugueseSequence(selectedBytes))



