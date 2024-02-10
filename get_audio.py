
import urllib.request
import pyaudio
import socket
from numpy.fft import fft, ifft
import time
import wave
import speech_recognition as sr
import matplotlib.pyplot as plt
import os

audio_path = os.getcwd() + '\\audio_record\\audio.wav'

FORMAT = 32
UDP_PORT = 4321
RATE = 16000

hostname=socket.gethostname()
UDP_IP=socket.gethostbyname(hostname)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

p = pyaudio.PyAudio()

r = sr.Recognizer()

def request(ESP_IP):
    try:
        response = urllib.request.urlopen("http://" + ESP_IP + "/getaudio")
    except Exception as e:
        return f"{ESP_IP} ERROR : {e}"
    else:
        return decoding_html(response)

def decoding_html(response):
    configs_string = str(response.read())[2:-1]
    configs = configs_string.split(",")
    ESP32_config = {}
    for config in configs:
        [key, value] = config.split(":")
        ESP32_config[key]= int(value)
    return ESP32_config

def save(audio, path = audio_path):
    if type(audio) != bytes:
        return f"{audio} isn't byte type"
    else:
        waveFile = wave.open(path,"wb")
        waveFile.setnchannels(1)
        waveFile.setsampwidth(pyaudio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(audio)
        waveFile.close()
        return "audio saved"

def SpeechRecognition(path = audio_path):
    with sr.AudioFile(path) as source:
        record = r.record(source)
    try:
        return r.recognize_google(record, language="es-MX")
    except Exception:
        return "Don't understandable"

def main(ESP_IP="192.168.100.12"):
    
    ESP32_config = request(ESP_IP)

    stream = p.open(format   = ESP32_config["format"],
                    channels = 1,
                    rate     = 14000, #ESP32_config["fs"],
                    output   = True)
    
    while True:
        try:
            data = sock.recvfrom(ESP32_config["samples"])[0]
            stream.write(data)
        except Exception as e:
            break

if __name__ == "__main__":
    main()
    

    

