import threading
import time
from GPSSensor import GPSSensor
from RandomSyllabes import RandomSyllabes
import threading
import time
import asyncio
import concurrent.futures
import subprocess
import os
import datetime  # Certifique-se de importar datetime
import json


# Obtenha o timestamp atual como uma string
timestamp = str(int(time.time()))

contatoDir = f"contatos/{timestamp}"

if not os.path.exists("contatos"):
    os.makedirs("contatos")

# Crie a pasta "logs" se ela não existir
if not os.path.exists(contatoDir):
    os.makedirs(contatoDir)




def play_lista_de_texto(lista,sensorName):
    global timestamp
    if lista and len(lista) > 0:
        # mensagem = f"Contato através do sensor {sensorName}. Mensagem recebida: {' '.join(lista)}"
        mensagem = f"{' '.join(lista)}"
        data_atual = datetime.datetime.now().isoformat()
        arquivo_wav = f"{data_atual}_{sensorName}.wav"

        comandoAudio = f"espeak '{mensagem}' -v pt-br -s 100"
        comando = f"espeak '{mensagem}' -v pt-br -s 100 -w ./{contatoDir}/{arquivo_wav}"

        try:
            subprocess.run(comando, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(comandoAudio, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar o comando: {e}")


# play_lista_de_texto(['Iniciando','a','execução'],True)

randomSyllabes = RandomSyllabes()
gpsSensor = GPSSensor()

isRun = True

def onStart(serialInstance):
    global isRun
    isRun = True
    print(f'Iniciando o contato - Tempo de contato: {timeout} seguundos')



def onStop(data,sensorData):
    global isRun
    isRun = False
    print(f'Finalizando o contato')



data = []
def onData(gpsData):
    data.append(gpsData)
    # Seu código de processamento de dados aqui
    pass



def periodic_task():
    while isRun:
        if len(data)==0:
            continue  # Pula para a próxima iteração do loop
        print('Finalizando contato e iniciando análise')
        print(f"Tamanho do array após {timeout} segundos: {len(data)}")
        valoresAcelerometro = [subarray[0] for subarray in data]
        valoresGiroscopio = [subarray[1] for subarray in data]
        valoresInclinometro = [subarray[2] for subarray in data]
        valoresMagnetometro = [subarray[3] for subarray in data]
        valoresTimestamp = [subarray[4] for subarray in data]

        confidence = 75
        min_percent_over_threshold = 0.4
        fator_filtro = 0.75

        peaksAcelerometro = gpsSensor.find_peaks(valoresAcelerometro, confidence, min_percent_over_threshold)
        filtered_peaksAcelerometro = gpsSensor.filter_peaks(peaksAcelerometro, fator_filtro)
        if filtered_peaksAcelerometro is not None and isinstance(filtered_peaksAcelerometro, list) and len(
                filtered_peaksAcelerometro) > 0:
            gpsSensor.printResultTable("Acelerômetro", filtered_peaksAcelerometro, valoresTimestamp,
                                       min_percent_over_threshold)
            listText = randomSyllabes.generate(filtered_peaksAcelerometro, valoresTimestamp, min_percent_over_threshold)
            play_lista_de_texto(listText, 'Acelerômetro')

        peaksGiroscopio = gpsSensor.find_peaks(valoresGiroscopio, confidence, min_percent_over_threshold)
        filtered_peaksGiroscopio = gpsSensor.filter_peaks(peaksGiroscopio, fator_filtro)

        if filtered_peaksGiroscopio is not None and isinstance(filtered_peaksGiroscopio, list) and len(
                filtered_peaksGiroscopio) > 0:
            gpsSensor.printResultTable("Giroscópio", filtered_peaksGiroscopio, valoresTimestamp,
                                       min_percent_over_threshold)
            listText = randomSyllabes.generate(filtered_peaksGiroscopio, valoresTimestamp, min_percent_over_threshold)
            play_lista_de_texto(listText, 'Giroscópio')

        peaksInclinometro = gpsSensor.find_peaks(valoresInclinometro, confidence, min_percent_over_threshold)
        filtered_peaksInclinometro = gpsSensor.filter_peaks(peaksInclinometro, fator_filtro)

        if filtered_peaksInclinometro is not None and isinstance(filtered_peaksInclinometro, list) and len(
                filtered_peaksInclinometro) > 0:
            gpsSensor.printResultTable("Inclinômetro", filtered_peaksInclinometro, valoresTimestamp,
                                       min_percent_over_threshold)
            listText = randomSyllabes.generate(filtered_peaksInclinometro, valoresTimestamp, min_percent_over_threshold)
            play_lista_de_texto(listText, 'Inclinômetro')

        peaksMagnetometro = gpsSensor.find_peaks(valoresMagnetometro, confidence, min_percent_over_threshold)
        filtered_peaksMagnetometro = gpsSensor.filter_peaks(peaksMagnetometro, fator_filtro)

        if filtered_peaksMagnetometro is not None and isinstance(filtered_peaksMagnetometro, list) and len(
                filtered_peaksMagnetometro) > 0:
            gpsSensor.printResultTable("Magnetômetro", filtered_peaksMagnetometro, valoresTimestamp,
                                       min_percent_over_threshold)
            listText = randomSyllabes.generate(filtered_peaksMagnetometro, valoresTimestamp, min_percent_over_threshold)
            play_lista_de_texto(listText, 'Magnetômetro')


        time.sleep(2)  # Aguarde um segundo antes de executar novamente


# Instancie a classe que contém os métodos de encontrar e filtrar picos
timeout = 60
def sensor_task():
    gpsSensor.startSensor(onStart, onData, onStop, timeout)
    print("Sensor iniciado")

# Inicialize a primeira thread para a tarefa periódica
thread1 = threading.Thread(target=periodic_task)

# Inicialize a segunda thread para o sensor
thread2 = threading.Thread(target=sensor_task)

# Inicie ambas as threads
thread1.start()
thread2.start()

# Aguarde ambas as threads terminarem (opcional)
thread1.join()
thread2.join()
