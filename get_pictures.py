import cv2
import numpy as np
import urllib.request as url_request
import datetime as dt
import os
import psutil
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

def take_picture(ESP_IP = "192.168.3.24"):
  frame = picture_request("http://" + ESP_IP + "/getpicture")[1]
  cv2.imwrite("picture.jpg", frame)

def get_video_names(videos_dir = "videos/"):
  video_names = os.listdir(videos_dir)
  return sorted(video_names)
  
def disk_managment(videos_dir = "videos/"):
  disk_usage = psutil.disk_usage("/")
  free = disk_usage.free / 1024**3
  used = disk_usage.used / 1024**3
  total = disk_usage.total / 1024**3
  print(f"DISK STAT: free:{free:.2f}GB usage:{used:.2f}GB total:{total:.2f}GB")

  while free < 8:
    video_names = get_video_names()
    os.remove(videos_dir + video_names[0])
    free = psutil.disk_usage("/").free / 1024**3

                                          #Bytes
def main(ESP_IP, res, fps_limit, record, size_limit = 47000000, video_folder = 'videos/'):
  """
  w = RES_DIC[res]["w"]
  h = RES_DIC[res]["h"]

  res_status = url_request.urlopen("http://"  + ESP_IP + 
                                   "/setresolution"    +
                                   "?width="  + str(w) +
                                   "&height=" + str(h))
  """
  w = 1024
  h = 768
  BytesperPixels = 0.062
  timestamp_limit = size_limit / (w * h * BytesperPixels)
  leave = False
  while not leave:
    video_name = f"{dt.datetime.now().ctime()}.mp4"
    video = cv2.VideoWriter(video_folder + video_name, cv2.VideoWriter_fourcc(*'mp4v'), fps_limit, (w, h))
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
    disk_managment()

if __name__ == "__main__":
  argparser = ArgumentParser()
  argparser.add_argument("-i", "--esp_ips", nargs='+', help="ESP32 IP Addresses")
  argparser.add_argument("-q", "--quality", help="CAM Resolution quality: "+ str(RES_DIC.keys()), default="mid")
  argparser.add_argument("-f", "--fps_limit", help="FPS Limit", default="5")
  argparser.add_argument("-r", "--record", help="Record bool" , action="store_true")
  argparser.add_argument("-t", "--tele_bot", help="Tele Bot bool" , action="store_true")
  args = argparser.parse_args()
  
  if args.tele_bot:
    import tele_bot
    t_telegram = Thread(name="polling_thread", target=tele_bot.polling)
    t_telegram.start()
  
  threads = []
  for esp_device in args.esp_ips:
    threads.append(Thread(name="main_thread", target=main, args=(ESP_IP     := esp_device,
                                                                 res        := args.quality,
                                                                 fps_limit  := int(args.fps_limit),
                                                                 record     := args.record)))
  for thread in threads:
    thread.start()
