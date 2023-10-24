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
import numpy as np
import pandas as pd
import math


# Obtenha o timestamp atual como uma string
timestamp = str(int(time.time()))

contatoDir = f"contatos/{timestamp}"

if not os.path.exists("contatos"):
    os.makedirs("contatos")

# Crie a pasta "logs" se ela não existir
if not os.path.exists(contatoDir):
    os.makedirs(contatoDir)

confidence = 95
min_percent_over_threshold = 95
fator_filtro = 0.75


def calculate_q_factor(freqs, fft_magnitude):
    # Encontrar a frequência de ressonância (frequência com amplitude máxima)
    f_res = freqs[np.argmax(fft_magnitude)]

    # Encontrar a amplitude máxima
    max_magnitude = np.max(fft_magnitude)

    # Encontrar as frequências onde a magnitude é 1/sqrt(2) da magnitude máxima
    half_power_points = np.where(fft_magnitude >= max_magnitude / np.sqrt(2))[0]

    # Calcular a largura de banda (Delta f)
    if len(half_power_points) > 1:
        delta_f = freqs[half_power_points[-1]] - freqs[half_power_points[0]]
    else:
        return -1

    # Calcular e retornar o Fator de Qualidade (Q)
    Q = f_res / delta_f
    return Q

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
    - fft_phase: array com as fases dos valores da FFT.
    """
    # Tamanho do sinal
    N = len(data)

    # Número de pontos FFT
    if n_fft is None:
        n_fft = N

    # Calculando FFT usando NumPy
    fft_values = np.fft.fft(data, n=n_fft)

    # Normalizando os valores da FFT
    fft_values = fft_values[:n_fft // 2] / n_fft

    # Pegando a magnitude dos valores da FFT
    fft_magnitude = np.abs(fft_values)

    # Pegando a fase dos valores da FFT
    fft_phase = np.angle(fft_values)

    # Calculando as frequências correspondentes
    freqs = np.fft.fftfreq(n_fft, 1 / sampling_rate)[:n_fft // 2]

    Q = calculate_q_factor(freqs,fft_magnitude)

    return freqs, fft_magnitude, fft_phase,Q


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
gpsSensor = GPSSensor()

isRun = True

listOfResult = []


def onStart(serialInstance):
    global isRun
    isRun = True
    print(f'Iniciando o contato - Tempo de contato: {timeout} seguundos')


def find_incoherent_phases(phase_array, std_multiplier=2.1413):
    """
    Encontra pontos e frequências de incoerência na matriz de fases.

    Parâmetros:
    - phase_array: array 2D onde cada linha é um conjunto de fases para todas as frequências em um ponto no tempo.
    - std_multiplier: O número de desvios padrão usado para definir um valor como incoerente.

    Retorna:
    - incoherent_indices: Uma lista de arrays, onde o primeiro elemento é o índice do cálculo FFT e o segundo é uma lista com os índices das frequências incoerentes.
    """
    # Calcular a média e o desvio padrão das fases para cada frequência
    mean_phases = np.mean(phase_array, axis=0)
    std_phases = np.std(phase_array, axis=0)

    incoherent_indices = []

    # Verificar cada conjunto de fases para ver se ele é incoerente
    for i, phases in enumerate(phase_array):
        deviation = np.abs(phases - mean_phases)
        freq_indices = np.where(deviation > std_multiplier * std_phases)[0]

        if len(freq_indices) > 0:
            incoherent_indices.append([i, list(freq_indices)])

    return incoherent_indices




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


def printResultTable():
    global listOfResult,dataAQ,incoherent_indices_phasesA,incoherent_indices_phasesB
    # Imprimir o título
    print(f"Resultado: \n")

    # Imprimir o cabeçalho da tabela
    print("{:<10} {:<10} {:<25} {:<25} {:<20} {:<5} {:<5} {:<20} {:<10} {:<10} {:<10}".format('POS','SIZE', 'VAL', '%', 'ACT-VAL','CH','FREQNum','FREQValue','FRAME','iPhase','QFactor'))

    for iResult, result in enumerate(listOfResult):
        if not result or not result[0]:
            continue

        peakList = result[0]
        min_percent_over_threshold = result[1]
        channelName = result[2]
        indexFreq = result[3]
        freqValue = result[4]




        for i, obj in enumerate(peakList):
            hasIncoherentPhase = any(obj[2] == x[0] for x in incoherent_indices_phasesA) if channelName == 'A' else any(
                obj[2] == x[0] for x in incoherent_indices_phasesB)

            # if (int(obj[1])-int(obj[0]) ) > 5:
            #     continue

            print("{:<10} {:<10} {:<25} {:<25} {:<20} {:<5} {:<5} {:<20} {:<10} {:<10} {:<10}".format(
                obj[2],
                obj[1] - obj[0],
                obj[3],
                f"{obj[4]}%",
                math.floor((obj[4] / min_percent_over_threshold) - 1),
                channelName,
                indexFreq,
                freqValue,
                obj[2],
                hasIncoherentPhase,
                dataAQ[iResult]
            ))

    # Imprimir os dados da tabela

def iterateAndAnalysisFreqValues(dataFreqs,channelName,freqsList):
    global confidence,min_percent_over_threshold,fator_filtro,incoherent_indices_phasesA,incoherent_indices_phasesB,listOfResult
    """
    Itera por todos os índices de frequência e imprime os valores correspondentes.

    Parâmetros:
    - dataFreqs: array 2D que armazena os valores FFT.
    """
    num_freqs = len(dataFreqs[0])  # supõe que todas as linhas tenham o mesmo número de colunas
    for index in range(num_freqs):
        freq_values = getValuesByFreqIndex(dataFreqs, index)
        dynamicMin_percent_over_threshold = min_percent_over_threshold
        # print('dynamicMin_percent_over_threshold',dynamicMin_percent_over_threshold)
        peaksFreq = gpsSensor.find_peaks(freq_values, confidence, dynamicMin_percent_over_threshold)
        filtered_peaksFreq = gpsSensor.filter_peaks(peaksFreq, fator_filtro)
        if filtered_peaksFreq is not None and isinstance(filtered_peaksFreq, list) and len(
                filtered_peaksFreq) > 0:
            listOfResult.append([filtered_peaksFreq,dynamicMin_percent_over_threshold,channelName,index,freqsList[index]])
        else:
            listOfResult.append(None)
            # audioSensor.printResultTable(f"Channel {channelName} - Freq {index} [{freqsList[index]}]", filtered_peaksFreq,
            #                            min_percent_over_threshold)
            # listText = randomSyllabes.generate(filtered_peaksFreq, 440) #Lá
            # play_lista_de_texto(listText, 'Channel A')


def save_to_csv(freqsA, dataFreqsA, dataPhasesA, X,name,incoherent_indices_phases,dataAQ):
    # Criando um DataFrame a partir dos dados de frequência
    df = pd.DataFrame(dataFreqsA, columns=freqsA)

    # Inicializando as colunas com valores padrão
    df['AlteracaoFase'] = 0
    df['IndicesFreqComFaseAlterada'] = np.nan
    df['QFactor'] = dataAQ

    # Mapeando índices e frequências
    for entry in incoherent_indices_phases:
        fft_index, freq_indices = entry[0], entry[1]
        df.at[fft_index, 'AlteracaoFase'] = 1
        df.at[fft_index, 'IndicesFreqComFaseAlterada'] = freq_indices

    #df['Phase'] = dataPhasesA


    # Salvando o DataFrame como um arquivo CSV
    df.to_csv(f'fft_data_{X}_samples{name}.csv', index=False)


def onStop(data,sensorData):
    global isRun,dataAQ,dataFreqsA,freqsA,dataFreqsB,freqsB,incoherent_indices_phasesA,incoherent_indices_phasesB,dataPhasesA,dataPhasesB,X

    isRun = False

    incoherent_indices_phasesA = find_incoherent_phases(dataPhasesA);
    iterateAndAnalysisFreqValues(dataFreqsA, 'A', freqsA)
    save_to_csv(freqsA, dataFreqsA, dataPhasesA, X, 'Conversacao', incoherent_indices_phasesA,dataAQ)
    printResultTable()
    print(f'Finalizando o contato')


data = []

dataA = []
dataFreqsA = []
dataPhasesA = []
dataAQ = []
incoherent_indices_phasesA = []
X = 1024

freqsA = None
freqsB = None
def onData(gpsData):
    global data,dataA,freqsA,dataFreqsA,dataPhasesA,incoherent_indices_phasesA,X
    data.append(gpsData)
    valoresAcelerometro = [subarray[0] for subarray in data]
    dataA.extend(valoresAcelerometro)

    # Verificando se temos amostras suficientes para o FFT
    while len(dataA) >= X:
        # Extração das amostras iniciais
        dataSampleA = dataA[:X]

        # Remoção das amostras utilizadas
        dataA = dataA[X:]

        # Cálculo do FFT para os canais A e B
        freqsA, fft_valuesA,phase,Q = calculate_fft(dataSampleA, 500)

        dataFreqsA.append(fft_valuesA)
        dataPhasesA.append(phase)
        dataAQ.append(Q)

    # Seu código de processamento de dados aqui
    pass




def periodic_task():
    global isRun,fator_filtro,min_percent_over_threshold,confidence,data,dataA,dataFreqsA, freqsA,dataPhasesA,X,incoherent_indices_phasesA


    while isRun:

        # if len(dataFreqsA)==0 or len(dataFreqsA)<1000:
        #     continue  # Pula para a próxima iteração do loop
        #
        # incoherent_indices_phasesA = find_incoherent_phases(dataPhasesA);
        # iterateAndAnalysisFreqValues(dataFreqsA, 'A', freqsA)
        # save_to_csv(freqsA, dataFreqsA, dataPhasesA, X, 'Conversacao', incoherent_indices_phasesA)
        # printResultTable()
        #
        # dataPhasesA.clear()
        # dataFreqsA.clear()
        # data.clear()


        if len(data)==0:
            continue  # Pula para a próxima iteração do loop
        # print('Finalizando contato e iniciando análise')
        # print(f"Tamanho do array após {timeout} segundos: {len(data)}")
        valoresAcelerometro = [subarray[0] for subarray in data]
        valoresGiroscopio = [subarray[1] for subarray in data]
        valoresInclinometro = [subarray[2] for subarray in data]
        valoresMagnetometro = [subarray[3] for subarray in data]
        valoresTimestamp = [subarray[4] for subarray in data]



        peaksAcelerometro = gpsSensor.find_peaks(valoresAcelerometro, confidence, min_percent_over_threshold)
        filtered_peaksAcelerometro = gpsSensor.filter_peaks(peaksAcelerometro, fator_filtro)
        if filtered_peaksAcelerometro is not None and isinstance(filtered_peaksAcelerometro, list) and len(
                filtered_peaksAcelerometro) > 0:
            gpsSensor.printResultTable("Acelerômetro", filtered_peaksAcelerometro, valoresTimestamp,
                                       min_percent_over_threshold)
            listText = randomSyllabes.generate(filtered_peaksAcelerometro, 440) #Lá
            play_lista_de_texto(listText, 'Acelerômetro')

        peaksGiroscopio = gpsSensor.find_peaks(valoresGiroscopio, confidence, min_percent_over_threshold)
        filtered_peaksGiroscopio = gpsSensor.filter_peaks(peaksGiroscopio, fator_filtro)

        if filtered_peaksGiroscopio is not None and isinstance(filtered_peaksGiroscopio, list) and len(
                filtered_peaksGiroscopio) > 0:
            gpsSensor.printResultTable("Giroscópio", filtered_peaksGiroscopio, valoresTimestamp,
                                       min_percent_over_threshold)
            listText = randomSyllabes.generate(filtered_peaksGiroscopio, 528) #Dó
            play_lista_de_texto(listText, 'Giroscópio')

        peaksInclinometro = gpsSensor.find_peaks(valoresInclinometro, confidence, min_percent_over_threshold)
        filtered_peaksInclinometro = gpsSensor.filter_peaks(peaksInclinometro, fator_filtro)

        if filtered_peaksInclinometro is not None and isinstance(filtered_peaksInclinometro, list) and len(
                filtered_peaksInclinometro) > 0:
            gpsSensor.printResultTable("Inclinômetro", filtered_peaksInclinometro, valoresTimestamp,
                                       min_percent_over_threshold)
            listText = randomSyllabes.generate(filtered_peaksInclinometro, 587.33) #RÉ
            play_lista_de_texto(listText, 'Inclinômetro')

        peaksMagnetometro = gpsSensor.find_peaks(valoresMagnetometro, confidence, min_percent_over_threshold)
        filtered_peaksMagnetometro = gpsSensor.filter_peaks(peaksMagnetometro, fator_filtro)

        if filtered_peaksMagnetometro is not None and isinstance(filtered_peaksMagnetometro, list) and len(
                filtered_peaksMagnetometro) > 0:
            gpsSensor.printResultTable("Magnetômetro", filtered_peaksMagnetometro, valoresTimestamp,
                                       min_percent_over_threshold)
            listText = randomSyllabes.generate(filtered_peaksMagnetometro, 659.25) #Mi
            play_lista_de_texto(listText, 'Magnetômetro')

        data.clear()
        time.sleep(3)  # Aguarde um segundo antes de executar novamente


# Instancie a classe que contém os métodos de encontrar e filtrar picos
timeout = 11 # 5*60  #5x60s = 5min
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