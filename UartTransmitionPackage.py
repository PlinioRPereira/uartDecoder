# Each transmited package contains the structure: <header><rising gray sequence><Falling gray sequency>
# Header structure: **<4 bytes>**. Those 4 bytes are a random number of 32 bits
# Rising Gray sequence is a sequency of the numbers from 0 to 255 in gray code
# Falling Gray sequence is a sequency of the numbers 254 to 0 in gray code 
import struct

class UartTransmitionPackage:

    # This methode considers that the byte 4th is the most significant byte and byte 0th is the least
    def bytesToInt(self, byteList):
        if len(byteList) != 4:
            raise ValueError("The array must have exactely 4 bytes")        
        
        byteArray = bytes(byteList)
        number = struct.unpack('I', byteArray)[0]
        return number
    
    def getMessageHeader(self, byteArray):
        
        pattern = ['*','*','x','x','x','x','*','*', 0]
        for i in range(0, len(byteArray)-len(pattern)-1):                   
            if (chr(byteArray[i].value) == pattern[0] and 
                chr(byteArray[i+1].value) == pattern[1] and
                chr(byteArray[i+6].value) == pattern[6] and
                chr(byteArray[i+7].value) == pattern[7] and
                byteArray[i+8].value == pattern[8]):
                
                numberArray = [byteArray[i+2].value, byteArray[i+3].value, byteArray[i+4].value, byteArray[i+5].value]
                randomNumber = self.bytesToInt(numberArray)
                return randomNumber

        return 0 




