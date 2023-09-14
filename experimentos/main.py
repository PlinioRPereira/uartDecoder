from GPSSensor import GPSSensor
import time
import asyncio
import concurrent.futures


gpsSensor = GPSSensor()

timeout = 5
def onStart(serialInstance):
    print('Iniciou')


def onStop(data):
    print('Finalizou')
    print(f"Tamanho do array após {timeout} segundos: {len(data)}")
    valoresAcelerometro = [subarray[0] for subarray in data]
    valoresGiroscopio = [subarray[1] for subarray in data]
    valoresInclinometro = [subarray[2] for subarray in data]
    valoresMagnetometro = [subarray[3] for subarray in data]
    valoresTimestamp = [subarray[4] for subarray in data]

    peaks = gpsSensor.find_peaks(valoresAcelerometro)
    print('PEAKS',peaks)




def onData(data):
    print('Data:',data)


# Função que representa o "Block 01"
gpsSensor.startSensor(onStart, onData, onStop,3)



