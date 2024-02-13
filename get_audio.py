
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

p = pyaudio.PyAudio()

r = sr.Recognizer()

T_US = 62.5
UDPS = 1024

def request(ESP_IP, T_us = T_US, UDP_Samples = UDPS):
    
    try:
        response = urllib.request.urlopen("http://"           + ESP_IP            +  #IP Address 
                                          "/getaudio"         +                      #URI
                                          "?T_us"             + str(T_us)         +  #First Argument
                                          "&UDP_samples"      + str(UDP_Samples))    #Second Argument
    except Exception as e:
        raise f"{ESP_IP} ERROR : {e}" 

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

def main(ESP_IP="192.168.100.3"):
    
    request(ESP_IP)

    stream = p.open(format   = 32,
                    channels = 1,
                    rate     = int(1000000/T_US),
                    output   = True)
    
    UDP_IP = socket.gethostbyname(socket.gethostname())
    sock.bind((UDP_IP, 4321))

    while True:
        try:
            data = sock.recvfrom(UDPS)[0]
        except Exception as e:
            raise f"{ESP_IP} ERROR : {e}"
        else:
            stream.write(data)

if __name__ == "__main__":
    main()
    

    

