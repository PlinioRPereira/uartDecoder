import serial
import threading
import math
from datetime import datetime
import time
import numpy as np
from scipy.fftpack import fft
import copy

# Global variables
TIMEData = [0] * 8
ACCData = [0] * 8
GYROData = [0] * 8
AngleData = [0] * 8
MageticData = [0] * 8
FrameState = 0
Bytenum = 0
CheckSum = 0

t = [0] * 7
a = [0] * 3
w = [0] * 3
Angle = [0] * 3
Magnetic = [0] * 3



class GPSSensor:
    def __init__(self):
        self.refDate = None
        self.transformed_data_array = []
        self.data_array = []
        self.active = None

    def calculate_magnitude(self,x, y, z):
        return math.sqrt(x**2 + y**2 + z**2)

    def transform_data(self,sensor_data):
        accel_magnitude = self.calculate_magnitude(sensor_data[0], sensor_data[1], sensor_data[2])
        gyro_magnitude = self.calculate_magnitude(sensor_data[3], sensor_data[4], sensor_data[5])
        incline_magnitude = self.calculate_magnitude(sensor_data[6], sensor_data[7], sensor_data[8])
        magnetic_magnitude = self.calculate_magnitude(sensor_data[9], sensor_data[10], sensor_data[11])
        timestamp = sensor_data[-1]

        transformed_data = [accel_magnitude, gyro_magnitude, incline_magnitude, magnetic_magnitude, timestamp]
        return transformed_data

    def calculate_thresholds(self, gps_signal, confidence=95):
        alpha = 100 - (100 - confidence) / 2
        beta = (100 - confidence) / 2
        max_threshold = np.percentile(gps_signal, alpha)
        min_threshold = np.percentile(gps_signal, beta)
        return max_threshold, min_threshold
    def find_peaks(self,gps_signal, confidence=95, min_percent_over_threshold=10, sampleRate=500):
        max_threshold, min_threshold = self.calculate_thresholds(gps_signal, confidence)

        peak_intervals = []
        peak_start = None
        peak_value = None
        max_percent_over = 0
        max_percent_over_time = 0
        diff = 0

        # print("Threshold:", max_threshold,min_threshold)

        for i, sample in enumerate(gps_signal):
            is_peak = False


            # Check for positive peaks
            if sample > max_threshold and max_threshold != 0:
                diff = abs(sample - max_threshold)
                percent_over = (diff / max_threshold) * 100
                if max_percent_over < percent_over:
                    max_percent_over = percent_over
                    max_percent_over_time = i
                if percent_over >= min_percent_over_threshold:
                    is_peak = True

            # Check for negative peaks
            elif sample < min_threshold and min_threshold != 0:
                diff = abs(sample - min_threshold)
                percent_over = abs((diff / min_threshold)) * 100
                if max_percent_over < percent_over:
                    max_percent_over = percent_over
                    max_percent_over_time = i
                if percent_over >= min_percent_over_threshold:
                    is_peak = True

            if is_peak:
                if peak_start is None:
                    peak_start = i
                    peak_value = sample
                # No 'else' needed here since 'peak_start' will only be None at the beginning
            elif peak_start is not None:
                peak_end = i - 1
                max_peak_position = max_percent_over_time
                peak_intervals.append([peak_start, peak_end,max_peak_position, diff, max_percent_over])
                peak_start = None
                peak_end = None
                peak_value = None
                max_percent_over = 0

        return peak_intervals

    def filter_peaks(self,peak_intervals, x):
        if not peak_intervals:
            return []

        # Encontrar o menor e o maior valor de max_percent_over
        min_percent = min(peak[3] for peak in peak_intervals)
        max_percent = max(peak[3] for peak in peak_intervals)

        # Calcular o novo limite
        new_threshold = min_percent + (max_percent - min_percent) * x

        # Filtrar a lista de picos
        filtered_peaks = [peak for peak in peak_intervals if peak[3] > new_threshold]

        return filtered_peaks




    def updateBaseDate(self,sensorDate):
        date = datetime(year=2000+sensorDate[0], month=sensorDate[1], day=sensorDate[2],
                        hour=sensorDate[3], minute=sensorDate[4], second=sensorDate[5], microsecond=sensorDate[6]*1000)
        actualDate = datetime.now()
        delta = actualDate - date
        self.refDate = delta.total_seconds() * 1000  # Convert to milliseconds

    def getRealDate(self,sensorDate):
        if self.refDate is None:
            return 0
        date = datetime(year=2000+sensorDate[0], month=sensorDate[1], day=sensorDate[2],
                        hour=sensorDate[3], minute=sensorDate[4], second=sensorDate[5], microsecond=sensorDate[6]*1000)
        delta = date.timestamp() * 1000  # Convert to milliseconds
        return delta + self.refDate

# Functions
    def get_time(self,datahex):
        YYYY, MM, DD, HH, MN, SS, MSL, MSH = datahex
        MS = (MSH << 8 | MSL)
        return [YYYY, MM, DD, HH, MN, SS, MS]

    def get_acc(self,datahex):
        axl, axh, ayl, ayh, azl, azh,tmp1,tmp2 = datahex
        k_acc = 16.0
        acc_x = (axh << 8 | axl) / 32768.0 * k_acc
        acc_y = (ayh << 8 | ayl) / 32768.0 * k_acc
        acc_z = (azh << 8 | azl) / 32768.0 * k_acc
        if acc_x >= k_acc:
            acc_x -= 2 * k_acc
        if acc_y >= k_acc:
            acc_y -= 2 * k_acc
        if acc_z >= k_acc:
            acc_z -= 2 * k_acc
        return [acc_x, acc_y, acc_z]

    def get_gyro(self,datahex):
        wxl, wxh, wyl, wyh, wzl, wzh,tmp1,tmp2 = datahex
        k_gyro = 2000.0
        gyro_x = (wxh << 8 | wxl) / 32768.0 * k_gyro
        gyro_y = (wyh << 8 | wyl) / 32768.0 * k_gyro
        gyro_z = (wzh << 8 | wzl) / 32768.0 * k_gyro
        if gyro_x >= k_gyro:
            gyro_x -= 2 * k_gyro
        if gyro_y >= k_gyro:
            gyro_y -= 2 * k_gyro
        if gyro_z >= k_gyro:
            gyro_z -= 2 * k_gyro
        return [gyro_x, gyro_y, gyro_z]

    def get_angle(self,datahex):
        rxl, rxh, ryl, ryh, rzl, rzh,tmp1,tmp2 = datahex
        k_angle = 180.0
        angle_x = (rxh << 8 | rxl) / 32768.0 * k_angle
        angle_y = (ryh << 8 | ryl) / 32768.0 * k_angle
        angle_z = (rzh << 8 | rzl) / 32768.0 * k_angle
        if angle_x >= k_angle:
            angle_x -= 2 * k_angle
        if angle_y >= k_angle:
            angle_y -= 2 * k_angle
        if angle_z >= k_angle:
            angle_z -= 2 * k_angle
        return [angle_x, angle_y, angle_z]

    def get_magnetic(self,datahex):
        rxl, rxh, ryl, ryh, rzl, rzh,tmp1,tmp2 = datahex
        mag_x = (rxh << 8 | rxl)
        mag_y = (ryh << 8 | ryl)
        mag_z = (rzh << 8 | rzl)
        return [mag_x, mag_y, mag_z]

# Implementing the function parseSensorData
    def parseSensorData(self,inputdata):
        global FrameState, Bytenum, CheckSum, t, a, w, Angle, Magnetic
        result = []
        for data in inputdata:
            if FrameState == 0:
                if data == 0x55 and Bytenum == 0:
                    CheckSum = data
                    Bytenum = 1
                elif data == 0x50 and Bytenum == 1:
                    CheckSum += data
                    FrameState = 99
                    Bytenum = 2
                elif data == 0x51 and Bytenum == 1:
                    CheckSum += data
                    FrameState = 1
                    Bytenum = 2
                elif data == 0x52 and Bytenum == 1:
                    CheckSum += data
                    FrameState = 2
                    Bytenum = 2
                elif data == 0x53 and Bytenum == 1:
                    CheckSum += data
                    FrameState = 3
                    Bytenum = 2
                elif data == 0x54 and Bytenum == 1:
                    CheckSum += data
                    FrameState = 4
                    Bytenum = 2

            elif FrameState == 99:  # Time Data
                if Bytenum < 10:
                    TIMEData[Bytenum - 2] = data
                    CheckSum += data
                    Bytenum += 1
                else:
                    if data == (CheckSum & 0xff):
                        t = self.get_time(TIMEData)
                    CheckSum = 0
                    Bytenum = 0
                    FrameState = 0

            elif FrameState == 1:  # Acc Data
                if Bytenum < 10:
                    ACCData[Bytenum - 2] = data
                    CheckSum += data
                    Bytenum += 1
                else:
                    if data == (CheckSum & 0xff):
                        a = self.get_acc(ACCData)
                    CheckSum = 0
                    Bytenum = 0
                    FrameState = 0

            elif FrameState == 2:  # Gyro Data
                if Bytenum < 10:
                    GYROData[Bytenum - 2] = data
                    CheckSum += data
                    Bytenum += 1
                else:
                    if data == (CheckSum & 0xff):
                        w = self.get_gyro(GYROData)
                    CheckSum = 0
                    Bytenum = 0
                    FrameState = 0

            elif FrameState == 3:  # Angle Data
                if Bytenum < 10:
                    AngleData[Bytenum - 2] = data
                    CheckSum += data
                    Bytenum += 1
                else:
                    if data == (CheckSum & 0xff):
                        Angle = self.get_angle(AngleData)
                    CheckSum = 0
                    Bytenum = 0
                    FrameState = 0

            elif FrameState == 4:  # Magnetic Data
                if Bytenum < 10:
                    MageticData[Bytenum - 2] = data
                    CheckSum += data
                    Bytenum += 1
                else:
                    if data == (CheckSum & 0xff):
                        Magnetic = self.get_magnetic(MageticData)
                        if self.refDate is None and t[0]:
                            self.updateBaseDate(t)
                        result = a + w + Angle + Magnetic + [self.getRealDate(t)]
                    CheckSum = 0
                    Bytenum = 0
                    FrameState = 0


        return result  # This can be modified based on what you want to return


    # Function to handle reading from the sensor
    def read_from_port(self,ser,onData,timeout):
        start_time = time.time()
        progressCount = 0
        initied = False

        while True:
            elapsed_time = time.time() - start_time
            progress = math.floor((elapsed_time/timeout)*100);
            if progress!=progressCount:
                progressCount = progress;
                print(progress,'%')
            if self.active is None or elapsed_time >timeout:
                break

            reading = ser.read(33)
            if reading:
                parsed_data = self.parseSensorData(reading)
                if parsed_data and parsed_data[0]!=0 and parsed_data[1]!=0 and parsed_data[2]!=0:
                    self.data_array.append(parsed_data)
                    transformed_data = self.transform_data(parsed_data)
                    if onData and callable(onData):
                        onData(transformed_data)
                    self.transformed_data_array.append(transformed_data)

    def startSensor(self,onStart,onData,onStop,timeout = 5):
        ser = serial.Serial('/dev/ttyUSB0', 921600, timeout=0.5)
        if onStart and callable(onStart):
            onStart(ser)

        self.active = True

        # Starting thread to read data from sensor
        thread = threading.Thread(target=self.read_from_port, args=(ser,onData,timeout))
        thread.start()
        thread.join()  # Espera a thread terminar
        if onStop and callable(onStop):
            onStop(self.transformed_data_array,self.data_array)



    def stopSensor(self):
        self.active = None
        print('STOP')

    def printResultTable(self, title, byteObjArray, timestampList,min_percent_over_threshold):
        # Imprimir o título
        print(f"Table Title: {title}\n")

        # Imprimir o cabeçalho da tabela
        print("{:<10} {:<10} {:<20} {:<20} {:<20} {:<10}".format('POS','SIZE', 'VAL', '%', 'TIME','ACT-VAL'))

        # Imprimir os dados da tabela
        for i, obj in enumerate(byteObjArray):
            print("{:<10} {:<20} {:<20} {:<20} {:<10}".format(
                obj[2],
                obj[1]-obj[0],
                obj[3],
                f"{obj[4]}%",
                timestampList[obj[2]],
                math.floor((obj[4]/min_percent_over_threshold)-1),
            ))

