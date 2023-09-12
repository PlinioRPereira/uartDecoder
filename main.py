from UartDecoder import UartDecoder
from PeakFinder import PeakFinder

decoder = UartDecoder('./test-exp1.wav')
print("Preparando canal da sequencia de Gray:")
decoded_data = decoder.decode(1)
print("Preparado...")
utils = PeakFinder()

for iteracao in range(1, 6):
    confidence = 100-iteracao
    min_percent_over_threshold = 45
    peaks = utils.find_peaks(decoder.left_channel,confidence,min_percent_over_threshold)

    print("----------------------------------------------------------------------------")
    print("ITERAÇAO ",iteracao)

    print("Total de Picos:", len(peaks) )
    formatedPeaks = utils.format_peaks(peaks)
    # print("Lista de Picos:",formatedPeaks)
    # Decodificar os dados

    selectedBytes = utils.find_intersection(peaks, decoded_data)
    num_elements = len(selectedBytes)
    print(f"Iteração {iteracao}: foram selecionados {num_elements} bytes da sequencia de Gray, considerando a confiança de {confidence}% e um valor de pico acima de {min_percent_over_threshold}% do limiar (max e min)")
    utils.printtable(selectedBytes)


