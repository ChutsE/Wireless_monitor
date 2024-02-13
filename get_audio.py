
import urllib.request
import pyaudio
import socket
import time
import wave
import speech_recognition as sr
from numpy.fft import fft, ifft
import matplotlib.pyplot as plt
import os

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_PORT = 4321
UDP_IP = socket.gethostbyname(socket.gethostname())

p = pyaudio.PyAudio()

r = sr.Recognizer()

def request(ESP_IP):
    
    try:
        response = urllib.request.urlopen("http://"   + ESP_IP +        #IP Address 
                                          "/getaudio" +                 #URI
                                          "?IPClient" + UDP_IP +        #First Argument
                                          "&Port"     + str(UDP_PORT))  #Second Argument
    except Exception as e:
        raise f"{ESP_IP} ERROR : {e}"
    else:
        return decoding_html(response)

def decoding_html(response):
    configs_string = str(response.read())[2:-1]
    configs = configs_string.split(",")
    ESP32_audio_config = {}
    for config in configs:
        [key, value] = config.split(":")
        ESP32_audio_config[key]= int(value)
    return ESP32_audio_config

def save(audio, format, rate, path = os.getcwd() + '\\audio_record\\audio.wav'):
    if type(audio) != bytes:
        return f"{audio} isn't byte type"
    else:
        waveFile = wave.open(path,"wb")
        waveFile.setnchannels(1)
        waveFile.setsampwidth(pyaudio.get_sample_size(format))
        waveFile.setframerate(rate)
        waveFile.writeframes(audio)
        waveFile.close()
        return "audio saved"

def SpeechRecognition(path = os.getcwd() + '\\audio_record\\audio.wav'):
    with sr.AudioFile(path) as source:
        record = r.record(source)
    try:
        return r.recognize_google(record, language="es-MX")
    except Exception:
        return "Don't understandable"

def main(ESP_IP="192.168.100.12"):
    
    ESP32_audio_config = request(ESP_IP)

    stream = p.open(format   = ESP32_audio_config["format"],
                    channels = 1,
                    rate     = ESP32_audio_config["fs"],
                    output   = True)
    
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        try:
            data = sock.recvfrom(ESP32_audio_config["samples"])[0]
        except Exception as e:
            raise f"{ESP_IP} ERROR : {e}"
        else:
            stream.write(data)

if __name__ == "__main__":
    main()
    

    

