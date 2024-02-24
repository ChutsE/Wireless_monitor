import cv2
import numpy as np
import urllib.request as url_request
import datetime as dt
from time import time as tm
from argparse import ArgumentParser
from threading import Thread


RES_DIC = {
  "low":       {"w": 320,  "h": 240},
  "low-mid":   {"w": 640,  "h": 480},
  "mid":       {"w": 800,  "h": 600},
  "mid-high":  {"w": 1024, "h": 768},
  "high":      {"w": 1280, "h": 1024},
  "very-high": {"w": 1600, "h": 1200}
}

def picture_request(url):
  try:
    img_resp = url_request.urlopen(url).read()
  except Exception as e:
    print(e)
    frame = None
    ret = False
  else:
    imgnp  = np.array(bytearray(img_resp),dtype=np.uint8)
    frame = cv2.imdecode(imgnp,-1)
    ret = True
  finally:
    return ret, frame

def print_text(fps, date, time, image):
    if time.hour >= 19 or time.hour <= 6:
       color = (255,255,255)
    else:
       color = (0,0,0)
    text = f"{int(fps)} FPS  {date.day}/{date.month}/{date.year}  {time.hour}:{time.minute}:{time.second}"
    font = cv2.FONT_HERSHEY_SIMPLEX
            #   imagen  ,texto ,coordenadas,fuente,tamano  ,BRG    ,grosor
    cv2.putText(image   ,text  ,(30,30)    ,font  ,0.5     ,color  , 1)
    return image

def take_picture(ESP_IP = "192.168.100.3"):
  frame = picture_request("http://" + ESP_IP + "/getpicture")[1]
  cv2.imwrite("picture.jpg", frame)

def main(ESP_IP, res, fps_limit, record, video_hours = 1, video_folder = 'videos/'):
  
  w = RES_DIC[res]["w"]
  h = RES_DIC[res]["h"]

  res_status = url_request.urlopen("http://"  + ESP_IP + 
                                   "/setresolution"    +
                                   "?width="  + str(w) +
                                   "&height=" + str(h))
  leave = False
  while not leave:
    video_name = f"{dt.datetime.now().ctime()}.mp4"
    video = cv2.VideoWriter(video_folder + video_name, cv2.VideoWriter_fourcc(*'mp4v'), fps_limit, (w, h))
    timestamp_limit = 3600 * video_hours * fps_limit
    timestamp = 0
    fps = 0
    t_prev = tm()
    while timestamp_limit > timestamp:
      ret, frame = picture_request("http://" + ESP_IP + "/getpicture")
      if ret:

        date_and_time = dt.datetime.now()
        cv2.imshow("video", print_text(fps, date_and_time.date(), date_and_time.time(), frame))

        if record:
          video.write(frame)

        if (cv2.waitKey(1) == ord("s")):
          leave = True
          break

        while(tm() - t_prev) < (1/(fps_limit+1)):
          pass

        t = tm()
        fps = 1 / (t - t_prev)
        t_prev = t
        
        timestamp += 1
        
    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
  argparser = ArgumentParser()
  argparser.add_argument("-i", "--esp_ip", help="ESP32 IP Address")
  argparser.add_argument("-q", "--quality", help="CAM Resolution quality: "+str(RES_DIC.keys()))
  argparser.add_argument("-f", "--fps_limit", help="FPS Limit")
  argparser.add_argument("-r", "--record", help="Record bool" , action="store_true")
  args = argparser.parse_args()
  
  import tele_bot
  t_telegram = Thread(name="polling_thread", target=tele_bot.polling)
  t_main = Thread(name="main_thread", target=main, args=(ESP_IP     := args.esp_ip,
                                                          res        := args.quality,
                                                          fps_limit  := int(args.fps_limit),
                                                          record     := args.record))
                      
  t_telegram.start()
  t_main.start()


