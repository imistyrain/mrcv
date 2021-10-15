import os
import sys
import cv2
import time
import datetime

interval = 1

def video2image(videopath):
    dir, videofile = os.path.split(os.path.abspath(videopath))
    videoname, _ = os.path.splitext(videofile)
    image_dir = dir + "/"+videoname
    cap = cv2.VideoCapture(videopath)
    index = 0
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    while True:
        ret, img = cap.read()
        if not ret:
            break
        sys.stdout.write("\rWriting "+str(index))
        sys.stdout.flush()
        index += 1
        if (index % interval != 0):
            continue
        if img.shape[0] < img.shape[1]:
            img = cv2.rotate(img, 0)
        img = cv2.resize(img, (720, 1280))
        #img = cv2.rotate(img, 2)
        time_str=time.strftime("%y%m%d_%H%M%S",time.localtime(time.time()))
        now = datetime.datetime.now()
        filename,_ = os.path.splitext(os.path.split(videopath)[1])
        cv2.imwrite(image_dir+"/"+filename+"_"+time_str+str(now)[-6:]+".jpg",img)

if __name__=="__main__":
    videopath = "test.mp4"
    if len(sys.argv) > 1:
        videopath = sys.argv[1]
    if len(sys.argv) > 2:
        interval = int(sys.argv[2])
    video2image(videopath)