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




def play_lista_de_texto(lista,sensorName):
    if lista and len(lista) > 0:
        mensagem = f"Contato através do sensor {sensorName}. Mensagem recebida: {' '.join(lista)}"
        data_atual = datetime.datetime.now().isoformat()
        arquivo_wav = f"{data_atual}.wav"

        comandoAudio = f"espeak '{mensagem}' -v pt-br -s 100"
        comando = f"espeak '{mensagem}' -v pt-br -s 100 -w {arquivo_wav}"

        try:
            subprocess.run(comando, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(comandoAudio, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar o comando: {e}")


# play_lista_de_texto(['Iniciando','a','execução'],True)

randomSyllabes = RandomSyllabes()
gpsSensor = GPSSensor()

def onStart(serialInstance):
    print(f'Iniciando o contato - Tempo de contato: {timeout} seguundos')


def onStop(data,sensorData):
    print('Finalizando contato e iniciando análise')
    print(f"Tamanho do array após {timeout} segundos: {len(data)}")
    valoresAcelerometro = [subarray[0] for subarray in data]
    valoresGiroscopio = [subarray[1] for subarray in data]
    valoresInclinometro = [subarray[2] for subarray in data]
    valoresMagnetometro = [subarray[3] for subarray in data]
    valoresTimestamp = [subarray[4] for subarray in data]

    confidence = 75
    min_percent_over_threshold = 0.3
    fator_filtro = 0.75

    logs = {
        "acc": {"list":valoresAcelerometro},
        "gir": {"list:":valoresGiroscopio},
        "inc": {"list":valoresInclinometro},
        "mag": {"list":valoresMagnetometro},
        "tim": valoresTimestamp,
    }
    peaksAcelerometro = gpsSensor.find_peaks(valoresAcelerometro,confidence,min_percent_over_threshold)
    filtered_peaksAcelerometro = gpsSensor.filter_peaks(peaksAcelerometro,fator_filtro)
    if filtered_peaksAcelerometro is not None and isinstance(filtered_peaksAcelerometro, list) and len(filtered_peaksAcelerometro) > 0:
        gpsSensor.printResultTable("Acelerômetro",filtered_peaksAcelerometro,valoresTimestamp,min_percent_over_threshold)
        listText = randomSyllabes.generate(filtered_peaksAcelerometro,valoresTimestamp,min_percent_over_threshold)
        play_lista_de_texto(listText, 'Acelerômetro')
        logs['acc']['peaks'] = peaksAcelerometro
        logs['acc']['filteredPeaks'] = filtered_peaksAcelerometro
        logs['acc']['syllabes'] = listText

    peaksGiroscopio = gpsSensor.find_peaks(valoresGiroscopio,confidence,min_percent_over_threshold)
    filtered_peaksGiroscopio = gpsSensor.filter_peaks(peaksGiroscopio,fator_filtro)

    if filtered_peaksGiroscopio is not None and isinstance(filtered_peaksGiroscopio, list) and len(filtered_peaksGiroscopio) > 0:
        gpsSensor.printResultTable("Giroscópio",filtered_peaksGiroscopio, valoresTimestamp,min_percent_over_threshold)
        listText = randomSyllabes.generate(filtered_peaksGiroscopio,valoresTimestamp,min_percent_over_threshold)
        play_lista_de_texto(listText,'Giroscópio')
        logs['gir']['peaks'] = peaksGiroscopio
        logs['gir']['filteredPeaks'] = filtered_peaksGiroscopio
        logs['gir']['syllabes'] = listText


    peaksInclinometro = gpsSensor.find_peaks(valoresInclinometro,confidence,min_percent_over_threshold)
    filtered_peaksInclinometro = gpsSensor.filter_peaks(peaksInclinometro,fator_filtro)

    if filtered_peaksInclinometro is not None and isinstance(filtered_peaksInclinometro, list) and len(filtered_peaksInclinometro) > 0:
        gpsSensor.printResultTable("Inclinômetro",filtered_peaksInclinometro, valoresTimestamp,min_percent_over_threshold)
        listText = randomSyllabes.generate(filtered_peaksInclinometro,valoresTimestamp,min_percent_over_threshold)
        play_lista_de_texto(listText,'Inclinômetro')
        logs['inc']['peaks'] = peaksInclinometro
        logs['inc']['filteredPeaks'] = filtered_peaksInclinometro
        logs['inc']['syllabes'] = listText


    peaksMagnetometro = gpsSensor.find_peaks(valoresMagnetometro,confidence,min_percent_over_threshold)
    filtered_peaksMagnetometro = gpsSensor.filter_peaks(peaksMagnetometro,fator_filtro)

    if filtered_peaksMagnetometro is not None and isinstance(filtered_peaksMagnetometro, list) and len(filtered_peaksMagnetometro) > 0:
        gpsSensor.printResultTable("Magnetômetro",filtered_peaksMagnetometro, valoresTimestamp,min_percent_over_threshold)
        listText = randomSyllabes.generate(filtered_peaksMagnetometro,valoresTimestamp,min_percent_over_threshold)
        play_lista_de_texto(listText,'Magnetômetro')
        logs['mag']['peaks'] = peaksMagnetometro
        logs['mag']['filteredPeaks'] = filtered_peaksMagnetometro
        logs['mag']['syllabes'] = listText

    # Crie a pasta "logs" se ela não existir
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Obtenha o timestamp atual como uma string
    timestamp = str(int(time.time()))

    # Crie o caminho do arquivo usando o timestamp e a extensão .json
    caminho_arquivo = os.path.join("logs", timestamp + ".json")

    # Abra o arquivo em modo de escrita e use json.dump() para escrever o dicionário como JSON
    with open(caminho_arquivo, "w") as arquivo_json:
        json.dump(logs, arquivo_json)

    print("Logs salvos com sucesso em", caminho_arquivo)



def onData(data):
    return
    # print('Data:',data)

timeout = 10

def main():
    global timeout
    print(f"Tentativa iniciada. O contato irá demorar {timeout} segundos.")
    # Função que representa o "Block 01"
    gpsSensor.startSensor(onStart, onData, onStop, timeout)

print("Iniciando a tentativa de contato em 5 segundos.")
tempo_de_atraso = 5
thread = threading.Timer(tempo_de_atraso, main)
# Inicie a contagem regressiva
thread.start()
# Espere até que a thread termine (opcional)
thread.join()
print("Terminando a execução do contato")







