import cv2
import numpy as np
import urllib.request
from time import time as tm

RES_DIC = {
    "low":      "320x240",
    "low-mid":  "800x600",
    "mid":      "1152x864",
    "mid-high": "1400x1050",
    "high":     "1600x1200"
}

def response_url(url):
    img_resp=urllib.request.urlopen(url)
    imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
    frame = cv2.imdecode(imgnp,-1)
    return  frame

def main(ESP_IP = "192.168.100.10", res = "mid"):
    
    res_status = urllib.request.urlopen("http://" + ESP_IP + "/setresolution?res=" + RES_DIC[res])
    print(res_status.read())
    t_prev = 0
    while True:
        frame = response_url("http://" + ESP_IP + "/getpicture")
        
        t = tm()
        diff_t = t - t_prev
        #print(f"FPS => {1/diff_t}")
        t_prev = t

        cv2.imshow("frame", frame)
        if(cv2.waitKey(1)==ord("s")):
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()



