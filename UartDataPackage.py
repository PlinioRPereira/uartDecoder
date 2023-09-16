# Each transmited package contains the structure: <header><rising gray sequence><Falling gray sequency>
# Header structure: **<4 bytes>**. Those 4 bytes are a random number of 32 bits
# Rising Gray sequence is a sequency of the numbers from 0 to 255 in gray code
# Falling Gray sequence is a sequency of the numbers 254 to 0 in gray code 
import struct

class UartDataPackage:

    def bytesToInt(self, byteArray):
        if len(byteArray) != 4:
            raise ValueError("The array must have exactely 4 bytes")        
        
        number = struct.unpack('I', byteArray)[0]
        return number
    
    def getMessageHeader(self, byteArray):
        
        pattern = ['*','*','x','x','x','x','*','*','0']
        for i in range(0, len(byteArray)-len(pattern)-1):
            if (byteArray[i] == pattern[i] and 
                byteArray[i+1] == pattern[i+1] and
                byteArray[i+6] == pattern[i+6] and
                byteArray[i+7] == pattern[i+7] and
                byteArray[i+8] == pattern[i+8]):
                
                nuberArray = [byteArray[i+2], byteArray[i+3], byteArray[i+4], byteArray[i+5]]
                randomNumber = self.bytesToInt(nuberArray)
                return randomNumber

        return 0 




