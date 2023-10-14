# import pyaudio
#
# p = pyaudio.PyAudio()
#
# info = p.get_host_api_info_by_index(0)
# numdevices = info.get('deviceCount')
#
# for i in range(0, numdevices):
#     if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
#         print("Input Device ID ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
#
# p.terminate()


import sounddevice as sd

devices = sd.query_devices()
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"Input Device ID {i} - {device['name']}")
