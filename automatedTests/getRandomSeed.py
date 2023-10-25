import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.abspath(''))

from UartDecoder import UartDecoder
from UartTransmitionPackage import UartTransmitionPackage

transmitionPackage = UartTransmitionPackage()

audioPath = 'C:/Users/DTI Digital/Documents/TVC/TVC_Data.wav'
print("Analisando o arquivo ", audioPath)
decoder = UartDecoder(audioPath)
decodedArray1 = decoder.decodeDataSlice(0, 10000)
decodedArray2 = decoder.decodeDataSlice(10000, 50000)

randomSeed1 = transmitionPackage.getMessageHeader(decodedArray1)
randomSeed2 = transmitionPackage.getMessageHeader(decodedArray2)

print("Random Seeds are: ", randomSeed1, randomSeed2) 

