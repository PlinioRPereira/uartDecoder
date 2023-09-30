import threading
import time
from AudioSensor import AudioSensor
from RandomSyllabes import RandomSyllabes
import threading
import time
import asyncio
import concurrent.futures
import subprocess
import os
import datetime  # Certifique-se de importar datetime
import json
import numpy as np
import math
import csv


def csv_to_json(csv_filename):
    # Inicializa um dicionário vazio para armazenar os resultados
    freq_dict = {}

    # Verifica se o arquivo existe
    if not os.path.exists(csv_filename):
        return freq_dict  # Retorna um JSON vazio

    try:
        # Abre o arquivo CSV e lê cada linha
        with open(csv_filename, 'r') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                freq_num = row['FREQNum'] + row['CH']
                percent_val = float(row['%'])

                # Se o freq_num já existe no dicionário, compara e mantém o maior valor
                if freq_num in freq_dict:
                    freq_dict[freq_num] = max(freq_dict[freq_num], percent_val)
                else:
                    freq_dict[freq_num] = percent_val
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return freq_dict  # Retorna um JSON vazio em caso de erro

    return freq_dict

jsonData = csv_to_json('./calibration_table.csv')

def getPercentual (index,defaultValue):
    return jsonData.get(index,defaultValue)




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

        comandoAudio = f"espeak '{mensagem}' -v mb-br2 -s 80"
        comando = f"espeak '{mensagem}' -v mb-br2 -s 80 -w ./{contatoDir}/{arquivo_wav}"

        try:
            subprocess.run(comando, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(comandoAudio, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar o comando: {e}")


# play_lista_de_texto(['Iniciando','a','execução'],True)

randomSyllabes = RandomSyllabes()
audioSensor = AudioSensor()

isRun = True


def calculate_fft(data, sampling_rate, n_fft=None):
    """
    Calcula a Transformada Rápida de Fourier (FFT) do array de dados fornecido.

    Parâmetros:
    - data: array de números representando o sinal.
    - sampling_rate: taxa de amostragem do sinal.
    - n_fft: número de pontos FFT. Se None, será usado o tamanho do array de dados.

    Retorna:
    - freqs: array com as frequências correspondentes.
    - fft_values: array com as magnitudes dos valores da FFT.
    """
    # Tamanho do sinal
    N = len(data)

    # Número de pontos FFT
    if n_fft is None:
        n_fft = N

    # Calculando FFT usando NumPy
    fft_values = np.fft.fft(data, n=n_fft)

    # Normalizando os valores da FFT
    fft_values = fft_values[:n_fft//2] / n_fft

    # Pegando a magnitude dos valores da FFT
    fft_values = np.abs(fft_values)

    # Calculando as frequências correspondentes
    freqs = np.fft.fftfreq(n_fft, 1/sampling_rate)[:n_fft//2]

    return freqs, fft_values


def onStart(serialInstance):
    global isRun
    isRun = True
    print(f'Iniciando o contato - Tempo de contato: {timeout} seguundos')


listOfResult = []


# [filtered_peaksFreq,min_percent_over_threshold,channelName,index,freqsList[index]]


def getMaxPercentByFreq(defaultPercent):
    global listOfResult
    # Imprimir o título
    print(f"Resultado: \n")

    # Imprimir o cabeçalho da tabela
    print("{:<10} {:<20} {:<20} {:<20} {:<5} {:<5} {:<20} {:<5}".format('POS', 'VAL', '%', 'ACT-VAL','CH','FREQNum','FREQValue','FRAME'))

    for iResult, result in enumerate(listOfResult):
        peakList = result[0]
        min_percent_over_threshold = result[1]
        channelName = result[2]
        indexFreq = result[3]
        freqValue = result[4]

        for i, obj in enumerate(peakList):
            print("{:<10} {:<20} {:<20} {:<20} {:<5} {:<5} {:<20} {:<5}".format(
                obj[2],
                obj[3],
                f"{obj[4]}%",
                math.floor((obj[4] / min_percent_over_threshold) - 1),
                channelName,
                indexFreq,
                freqValue,
                iResult,
            ))

    # Imprimir os dados da tabela


def printResultTable():
    global listOfResult
    # Imprimir o título
    print(f"Resultado: \n")

    # Imprimir o cabeçalho da tabela
    print("{:<10} {:<20} {:<20} {:<20} {:<5} {:<5} {:<20} {:<5}".format('POS', 'VAL', '%', 'ACT-VAL','CH','FREQNum','FREQValue','FRAME'))

    for iResult, result in enumerate(listOfResult):
        peakList = result[0]
        min_percent_over_threshold = result[1]
        channelName = result[2]
        indexFreq = result[3]
        freqValue = result[4]

        for i, obj in enumerate(peakList):
            print("{:<10} {:<20} {:<20} {:<20} {:<5} {:<5} {:<20} {:<5}".format(
                obj[2],
                obj[3],
                f"{obj[4]}%",
                math.floor((obj[4] / min_percent_over_threshold) - 1),
                channelName,
                indexFreq,
                freqValue,
                iResult,
            ))

    # Imprimir os dados da tabela

def getResultTable():
    global listOfResult

    fResult = []

    for iResult, result in enumerate(listOfResult):
        peakList = result[0]
        min_percent_over_threshold = result[1]
        channelName = result[2]
        indexFreq = result[3]
        freqValue = result[4]

        for i, obj in enumerate(peakList):
            fResult.append([
                obj[2],
                obj[3],
                obj[4],
                math.floor((obj[4] / min_percent_over_threshold) - 1),
                channelName,
                indexFreq,
                freqValue,
                iResult,
            ])
    return fResult


def saveResultTable():
    global listOfResult

    # Abre um novo arquivo CSV para escrita
    with open('calibration_table.csv', 'w', newline='') as csvfile:
        # Cria um escritor CSV
        csvwriter = csv.writer(csvfile)

        # Escreve o cabeçalho do CSV
        csvwriter.writerow(['POS', 'VAL', '%', 'ACT-VAL','CH','FREQNum','FREQValue','FRAME'])

        for iResult, result in enumerate(listOfResult):
            peakList = result[0]
            min_percent_over_threshold = result[1]
            channelName = result[2]
            indexFreq = result[3]
            freqValue = result[4]

            for i, obj in enumerate(peakList):
                # Escreve cada linha no CSV
                csvwriter.writerow([
                    obj[2],
                    obj[3],
                    obj[4],
                    math.floor((obj[4] / min_percent_over_threshold) - 1),
                    channelName,
                    indexFreq,
                    freqValue,
                    iResult,
                ])

def onStop(data,sensorData):
    global isRun,dataFreqsA,freqsA,dataFreqsB,freqsB
    isRun = False
    iterateAndAnalysisFreqValues(dataFreqsA, 'A', freqsA)
    iterateAndAnalysisFreqValues(dataFreqsB, 'B', freqsB)
    # saveResultTable()
    printResultTable()


    print(f'Finalizando o contato')




dataA = []
dataB = []

dataFreqsA = []
dataFreqsB = []

freqsA = None
freqsB = None

X = 1024  # Número de amostras para o FFT

def getValuesByFreqIndex(dataFreqs, index):
    """
    Obtém os valores de uma frequência específica de um array 2D (cada linha representa uma transformada FFT).

    Parâmetros:
    - dataFreqs: array 2D que armazena os valores FFT.
    - index: índice da frequência desejada.

    Retorna:
    - freq_values: array com os valores da frequência especificada ao longo do tempo.
    """
    freq_values = [freqs[index] for freqs in dataFreqs]
    return freq_values


confidence = 95
min_percent_over_threshold = 0.5
fator_filtro = 0.80


def iterateAndAnalysisFreqValues(dataFreqs,channelName,freqsList):
    global confidence,min_percent_over_threshold,fator_filtro
    """
    Itera por todos os índices de frequência e imprime os valores correspondentes.

    Parâmetros:
    - dataFreqs: array 2D que armazena os valores FFT.
    """
    num_freqs = len(dataFreqs[0])  # supõe que todas as linhas tenham o mesmo número de colunas
    for index in range(num_freqs):
        freq_values = getValuesByFreqIndex(dataFreqs, index)
        dynamicMin_percent_over_threshold = math.ceil(getPercentual(str(index)+channelName,min_percent_over_threshold))
        print('dynamicMin_percent_over_threshold',dynamicMin_percent_over_threshold)
        peaksFreq = audioSensor.find_peaks(freq_values, confidence, dynamicMin_percent_over_threshold)
        filtered_peaksFreq = audioSensor.filter_peaks(peaksFreq, fator_filtro)
        if filtered_peaksFreq is not None and isinstance(filtered_peaksFreq, list) and len(
                filtered_peaksFreq) > 0:
            listOfResult.append([filtered_peaksFreq,dynamicMin_percent_over_threshold,channelName,index,freqsList[index]])
            # audioSensor.printResultTable(f"Channel {channelName} - Freq {index} [{freqsList[index]}]", filtered_peaksFreq,
            #                            min_percent_over_threshold)
            # listText = randomSyllabes.generate(filtered_peaksFreq, 440) #Lá
            # play_lista_de_texto(listText, 'Channel A')




def onData(channelA, channelB):
    global dataA, dataB,dataFreqsA,dataFreqsB, freqsA,freqsB,X

    # Acrescentando novos dados
    dataA.extend(channelA)
    dataB.extend(channelB)

    # Verificando se temos amostras suficientes para o FFT
    while len(dataA) >= X:
        # Extração das amostras iniciais
        dataSampleA = dataA[:X]

        # Remoção das amostras utilizadas
        dataA = dataA[X:]

        # Cálculo do FFT para os canais A e B
        freqsA, fft_valuesA = calculate_fft(dataSampleA, 44100)

        dataFreqsA.append(fft_valuesA)

    while len(dataB) >= X:
        # Extração das amostras iniciais
        dataSampleB = dataB[:X]

        # Remoção das amostras utilizadas
        dataB = dataB[X:]

        # Cálculo do FFT para os canais A e B
        freqsB, fft_valuesB = calculate_fft(dataSampleB, 44100)

        dataFreqsB.append(fft_valuesB)


def periodic_task():
    global dataA, dataB,dataFreqsA,dataFreqsB, freqsA,freqsB

    # while isRun:
    #     if len(dataFreqsA) > 0 and len(dataFreqsA[0]) > 0:
    #         iterateAndAnalysisFreqValues(dataFreqsA, 'A', freqsA)
    #         dataFreqsA.clear()
    #
    #     if len(dataFreqsB) > 0 and len(dataFreqsB[0]) > 0:
    #         iterateAndAnalysisFreqValues(dataFreqsB, 'B', freqsB)
    #         dataFreqsB.clear()
    #
    #     # print('FeqsA',freqsA)
    #     # print('dataFreqsA',dataFreqsA)
    #     #
    #     # print('freqsB',freqsB)
    #     # print('dataFreqsB',dataFreqsB)
    #     # if len(dataA)==0:
    #     #     continue  # Pula para a próxima iteração do loop
    #     # # print('Finalizando contato e iniciando análise')
    #     # # print(f"Tamanho do array após {timeout} segundos: {len(data)}")
    #     # # valoresAcelerometro = [subarray[0] for subarray in data]
    #     # # valoresGiroscopio = [subarray[1] for subarray in data]
    #     # # valoresInclinometro = [subarray[2] for subarray in data]
    #     # # valoresMagnetometro = [subarray[3] for subarray in data]
    #     # # valoresTimestamp = [subarray[4] for subarray in data]
    #     # #
    #     # confidence = 99
    #     # min_percent_over_threshold = 70
    #     # fator_filtro = 0.80
    #     #
    #     # peaksChannelA = audioSensor.find_peaks(dataA, confidence, min_percent_over_threshold)
    #     # filtered_peaksChannelA = audioSensor.filter_peaks(peaksChannelA, fator_filtro)
    #     # if filtered_peaksChannelA is not None and isinstance(filtered_peaksChannelA, list) and len(
    #     #         filtered_peaksChannelA) > 0:
    #     #     audioSensor.printResultTable("Channel A", filtered_peaksChannelA,
    #     #                                min_percent_over_threshold)
    #     #     listText = randomSyllabes.generate(filtered_peaksChannelA, 440) #Lá
    #     #     play_lista_de_texto(listText, 'Channel A')
    #     #
    #     # peaksChannelB = audioSensor.find_peaks(dataB, confidence, min_percent_over_threshold)
    #     # filtered_peaksChannelB = audioSensor.filter_peaks(peaksChannelB, fator_filtro)
    #     # if filtered_peaksChannelB is not None and isinstance(filtered_peaksChannelB, list) and len(
    #     #         filtered_peaksChannelB) > 0:
    #     #     audioSensor.printResultTable("Channel B", filtered_peaksChannelB,
    #     #                                min_percent_over_threshold)
    #     #     listText = randomSyllabes.generate(filtered_peaksChannelB, 523.25) #Lá
    #     #     play_lista_de_texto(listText, 'Channel B')
    #     #
    #     #
    #     # #
    #     # # peaksAcelerometro = gpsSensor.find_peaks(valoresAcelerometro, confidence, min_percent_over_threshold)
    #     # # filtered_peaksAcelerometro = gpsSensor.filter_peaks(peaksAcelerometro, fator_filtro)
    #     # # if filtered_peaksAcelerometro is not None and isinstance(filtered_peaksAcelerometro, list) and len(
    #     # #         filtered_peaksAcelerometro) > 0:
    #     # #     gpsSensor.printResultTable("Acelerômetro", filtered_peaksAcelerometro, valoresTimestamp,
    #     # #                                min_percent_over_threshold)
    #     # #     listText = randomSyllabes.generate(filtered_peaksAcelerometro, valoresTimestamp, 440) #Lá
    #     # #     play_lista_de_texto(listText, 'Acelerômetro')
    #     # #
    #     # # peaksGiroscopio = gpsSensor.find_peaks(valoresGiroscopio, confidence, min_percent_over_threshold)
    #     # # filtered_peaksGiroscopio = gpsSensor.filter_peaks(peaksGiroscopio, fator_filtro)
    #     # #
    #     # # if filtered_peaksGiroscopio is not None and isinstance(filtered_peaksGiroscopio, list) and len(
    #     # #         filtered_peaksGiroscopio) > 0:
    #     # #     gpsSensor.printResultTable("Giroscópio", filtered_peaksGiroscopio, valoresTimestamp,
    #     # #                                min_percent_over_threshold)
    #     # #     listText = randomSyllabes.generate(filtered_peaksGiroscopio, valoresTimestamp, 523.25) #Dó
    #     # #     play_lista_de_texto(listText, 'Giroscópio')
    #     # #
    #     # # peaksInclinometro = gpsSensor.find_peaks(valoresInclinometro, confidence, min_percent_over_threshold)
    #     # # filtered_peaksInclinometro = gpsSensor.filter_peaks(peaksInclinometro, fator_filtro)
    #     # #
    #     # # if filtered_peaksInclinometro is not None and isinstance(filtered_peaksInclinometro, list) and len(
    #     # #         filtered_peaksInclinometro) > 0:
    #     # #     gpsSensor.printResultTable("Inclinômetro", filtered_peaksInclinometro, valoresTimestamp,
    #     # #                                min_percent_over_threshold)
    #     # #     listText = randomSyllabes.generate(filtered_peaksInclinometro, valoresTimestamp, 587.33) #RÉ
    #     # #     play_lista_de_texto(listText, 'Inclinômetro')
    #     # #
    #     # # peaksMagnetometro = gpsSensor.find_peaks(valoresMagnetometro, confidence, min_percent_over_threshold)
    #     # # filtered_peaksMagnetometro = gpsSensor.filter_peaks(peaksMagnetometro, fator_filtro)
    #     # #
    #     # # if filtered_peaksMagnetometro is not None and isinstance(filtered_peaksMagnetometro, list) and len(
    #     # #         filtered_peaksMagnetometro) > 0:
    #     # #     gpsSensor.printResultTable("Magnetômetro", filtered_peaksMagnetometro, valoresTimestamp,
    #     # #                                min_percent_over_threshold)
    #     # #     listText = randomSyllabes.generate(filtered_peaksMagnetometro, valoresTimestamp, 659.25) #Mi
    #     # #     play_lista_de_texto(listText, 'Magnetômetro')
    #     # print('ShowDataA,',len(dataA))
    #     # print('ShowDataB,',len(dataB))
    #     #
    #     # dataA.clear()
    #     # dataB.clear()
    #     time.sleep(2)  # Aguarde um segundo antes de executar novamente





# Instancie a classe que contém os métodos de encontrar e filtrar picos
timeout = 60  #5x60s = 5min
def sensor_task():
    audioSensor.startSensor(onStart, onData, onStop, timeout)
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
