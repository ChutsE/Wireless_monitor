import cv2
import numpy as np
import urllib.request as url_request
from time import time as tm
import datetime as dt

RES_DIC = {
  "low":       {"w": "320",  "h": "240"},
  "low-mid":   {"w": "640",  "h": "480"},
  "mid":       {"w": "800",  "h": "600"},
  "mid-high":  {"w": "1024", "h": "768"},
  "high":      {"w": "1280", "h": "1024"},
  "very-high": {"w": "1600", "h": "1200"}
}

def response_url(url):
  status = None
  img_resp = url_request.urlopen(url).read()
  if len(img_resp) < 100:
    status = img_resp
  else:
    imgnp  =np.array(bytearray(img_resp),dtype=np.uint8)
    frame = cv2.imdecode(imgnp,-1)
  return frame, status

def print_text(fps, date, time, image):
    
    text = f"{int(fps)} FPS  {date.day}/{date.month}/{date.year}  {time.hour}:{time.minute}:{time.second}"
    font = cv2.FONT_HERSHEY_SIMPLEX
            #   imagen  ,texto ,coordenadas,fuente,tamano  ,BRG        ,grosor
    cv2.putText(image   ,text  ,(30,30)    ,font  ,1     ,(0,0,0), 2)
    return image

def main(ESP_IP = "192.168.100.10", res = "mid-high"):

  #res_status = url_request.urlopen("http://" + ESP_IP + "/setresolution?res=" + RES_DIC[res])
  #print(res_status.read())
  
  #time.sleep(1)
  
  timestamp = 0
  fps = 0
  t_prev = tm()
  while True:
    date_and_time = dt.datetime.now()
    date = date_and_time.date()
    time = date_and_time.time()
    frame, status = response_url("http://" + ESP_IP + "/getpicture")

    if (tm() - t_prev) < 1:
      timestamp += 1
    else:
      fps = timestamp
      timestamp = 0
      t_prev = tm()
      
    if (cv2.waitKey(1) == ord("s")) or (status != None):
      break
    cv2.imshow("frame", print_text(fps, date, time, frame))

  cv2.destroyAllWindows()

if __name__ == "__main__":
    main()



