import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.abspath(''))

from UartDecoder import UartDecoder

audioPath = 'C:/Users/DTI Digital/Documents/TVC/TVC_Data.wav'
print("Analisando o arquivo ", audioPath)
decoder = UartDecoder(audioPath)
decodedArray = decoder.decodeDataSlice(0, 100000)
decoder.printByteStructArray(decodedArray)

