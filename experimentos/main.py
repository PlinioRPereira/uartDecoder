from GPSSensor import GPSSensor
from RandomSyllabes import RandomSyllabes
import time
import asyncio
import concurrent.futures


randomSyllabes = RandomSyllabes()
gpsSensor = GPSSensor()

timeout = 5
def onStart(serialInstance):
    print(f'Iniciando o contato - Tempo de contato: {timeout} seguundos')


def onStop(data):
    print('Finalizando contato e iniciando análise')
    print(f"Tamanho do array após {timeout} segundos: {len(data)}")
    valoresAcelerometro = [subarray[0] for subarray in data]
    valoresGiroscopio = [subarray[1] for subarray in data]
    valoresInclinometro = [subarray[2] for subarray in data]
    valoresMagnetometro = [subarray[3] for subarray in data]
    valoresTimestamp = [subarray[4] for subarray in data]

    confidence = 75
    min_percent_over_threshold = 0.5
    fator_filtro = 0.75

    peaksAcelerometro = gpsSensor.find_peaks(valoresAcelerometro,confidence,min_percent_over_threshold)
    filtered_peaksAcelerometro = gpsSensor.filter_peaks(peaksAcelerometro,fator_filtro)
    if filtered_peaksAcelerometro is not None and isinstance(filtered_peaksAcelerometro, list) and len(filtered_peaksAcelerometro) > 0:
        gpsSensor.printResultTable("Acelerômetro",filtered_peaksAcelerometro,valoresTimestamp)
        randomSyllabes.generate(filtered_peaksAcelerometro,valoresTimestamp)


    peaksGiroscopio = gpsSensor.find_peaks(valoresGiroscopio,confidence,min_percent_over_threshold)
    filtered_peaksGiroscopio = gpsSensor.filter_peaks(peaksGiroscopio,fator_filtro)

    if filtered_peaksGiroscopio is not None and isinstance(filtered_peaksGiroscopio, list) and len(filtered_peaksGiroscopio) > 0:
        gpsSensor.printResultTable("Giroscópio",filtered_peaksGiroscopio, valoresTimestamp)
        randomSyllabes.generate(filtered_peaksGiroscopio,valoresTimestamp)


    peaksInclinometro = gpsSensor.find_peaks(valoresInclinometro,confidence,min_percent_over_threshold)
    filtered_peaksInclinometro = gpsSensor.filter_peaks(peaksInclinometro,fator_filtro)

    if filtered_peaksInclinometro is not None and isinstance(filtered_peaksInclinometro, list) and len(filtered_peaksInclinometro) > 0:
        gpsSensor.printResultTable("Inclinômetro",filtered_peaksInclinometro, valoresTimestamp)
        randomSyllabes.generate(filtered_peaksInclinometro,valoresTimestamp)

    peaksMagnetometro = gpsSensor.find_peaks(valoresMagnetometro,confidence,min_percent_over_threshold)
    filtered_peaksMagnetometro = gpsSensor.filter_peaks(peaksMagnetometro,fator_filtro)

    if filtered_peaksMagnetometro is not None and isinstance(filtered_peaksMagnetometro, list) and len(filtered_peaksMagnetometro) > 0:
        gpsSensor.printResultTable("Magnetômetro",filtered_peaksMagnetometro, valoresTimestamp)
        randomSyllabes.generate(filtered_peaksMagnetometro,valoresTimestamp)


def onData(data):
    return
    # print('Data:',data)


# Função que representa o "Block 01"
gpsSensor.startSensor(onStart, onData, onStop,3)



