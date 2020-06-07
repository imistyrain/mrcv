#coding=utf-8
import sys
import cv2
import numpy as np

# 已知颜色列表，可以将其过滤不显示在最终图上
known_colors ={(0,0,0),(255,255,255)
    #,(255,0,0),(0,255,0),(0,0,255)
    }

def watch(img, scale = 80):
    h, w, c = img.shape
    show = cv2.resize(img,(w*scale,h*scale),interpolation = cv2.INTER_NEAREST)
    for i in range(h):
        for j in range(w):
            color = tuple(img[i,j])
            if not color in known_colors:
                cm = np.min(img[i,j])
                b = int(255 - cm)
                g = int(255 - cm)
                r = int(255 - cm)
                color = (b,g,r)
                cv2.putText(show,str(j)+","+str(i),(int(j*scale),int(i*scale)+15),1,1,color)
                for k in range(c):
                    cv2.putText(show,str(img[i,j,k]),(int(j*scale),int(i*scale)+k*20+35),1,1,(0,0,0))
    cv2.imwrite("watch.png",show)

if __name__=="__main__":
    imgpath = "opencv.png"
    if len(sys.argv) > 1:
        imgpath = sys.argv[1]
    img = cv2.imread(imgpath)
    watch(img)