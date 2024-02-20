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
  img_resp = url_request.urlopen(url).read()
  imgnp  =np.array(bytearray(img_resp),dtype=np.uint8)
  frame = cv2.imdecode(imgnp,-1)
  return frame

def print_text(fps, date, time, image):
    
    text = f"{int(fps)} FPS  {date.day}/{date.month}/{date.year}  {time.hour}:{time.minute}:{time.second}"
    font = cv2.FONT_HERSHEY_SIMPLEX
            #   imagen  ,texto ,coordenadas,fuente,tamano  ,BRG        ,grosor
    cv2.putText(image   ,text  ,(30,30)    ,font  ,0.5     ,(0,0,0), 1)
    return image

def main(ESP_IP = "192.168.100.10", res = "high", fps_limit = 7, path_video = 'video_record\\video.mp4'):

  res_status = url_request.urlopen("http://" + ESP_IP + 
                                   "/setresolution"  +
                                   "?width=" + RES_DIC[res]["w"] +
                                   "&height=" + RES_DIC[res]["h"])

  writer = cv2.VideoWriter(path_video, cv2.VideoWriter_fourcc(*'XIVX'), 10, (int(RES_DIC[res]["w"]), int(RES_DIC[res]["h"])))

  fps = 0
  t_prev = tm()
  while True:
    date_and_time = dt.datetime.now()
    date = date_and_time.date()
    time = date_and_time.time()
    frame = response_url("http://" + ESP_IP + "/getpicture")

    cv2.imshow("frame", print_text(fps, date, time, frame))
    writer.write(frame)

    if (cv2.waitKey(1) == ord("s")):
      break

    while(tm() - t_prev) < (1/(fps_limit+1)):
      pass

    t = tm()
    fps = 1 / (t - t_prev)
    t_prev = t

  writer.release()
  cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


