import os
import sys
import cv2
import time
import datetime

def video2image(videopath, image_dir = "images"):
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
        if img.shape[0] < img.shape[1]:
            img = cv2.rotate(img,0)
        time_str=time.strftime("%y%m%d_%H%M%S",time.localtime(time.time()))
        now = datetime.datetime.now()
        filename,_ = os.path.splitext(os.path.split(videopath)[1])
        cv2.imwrite(image_dir+"/"+filename+"_"+time_str+str(now)[-6:]+".jpg",img)
        index += 1

if __name__=="__main__":
    videopath = "test.mp4"
    image_dir = "images"
    if len(sys.argv) > 1:
        videopath = sys.argv[1]
    if len(sys.argv) > 2:
        image_dir = sys.argv[2]
    video2image(videopath, image_dir)