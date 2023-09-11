from UartDecoder import UartDecoder
from PeakFinder import PeakFinder

decoder = UartDecoder('./test-exp1.wav')
utils = PeakFinder()

confidence = 95
min_percent_over_threshold = 25
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
