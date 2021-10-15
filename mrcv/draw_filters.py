import os
import sys
import cv2
import math
import numpy as np
import matplotlib.pyplot as plt
import caffe
from tqdm import tqdm

def draw_filters(name, data):
    data = data.squeeze()
    shape = data.shape
    savedir = "filters/" + name
    if not os.path.exists(savedir):
        os.makedirs(savedir)
    #dview = np.abs(data)
    dview = data.copy()
    mind = dview.min()
    maxd = dview.max()
    dview -= mind
    dview /= (maxd - mind)
    if len(shape) == 1:
        width = int(np.sqrt(shape[0]))
        height = int(shape[0] / width)
        img = np.zeros((width*100,height*100,3),dtype=np.float32)
        for i in range(height):
            for j in range(width):
                index = i * height + j
                if index >= shape[0]:
                    break
                img[i*100:(i+1)*100,j*100:(j+1)*100,:] = dview[index] * 255
                v = round(data[i*width+j],6)
                x = j*100
                y = i*100+60
                cv2.putText(img,str(v),(x,y),1,1,(0,0,255))
        cv2.imwrite(savedir+"/"+name+".jpg",img)
        return
    width = shape[-1]
    height = shape[-2]
    if len(shape) == 4:
        for i in range(shape[0]):
            for j in range(shape[1]):
                img = np.zeros((height*100,width*100,3),dtype=np.float32)
                for h in range(height):
                    for w in range(width):
                        img[h*100:(h+1)*100,w*100:(w+1)*100,:]=dview[i][j][h][w]
                        v = round(data[i][j][h][w],5)
                        cv2.putText(img,str(v),(w*100,h*100+60),1,1,(0,0,255))
                savepath = savedir+"/"+str(i)+"_"+str(j)+".jpg"
                cv2.imwrite(savepath,img*255)
    elif len(shape) == 3:
        for i in range(shape[0]):
            img = np.zeros((height*100,width*100,3),dtype=np.float32)
            for h in range(height):
                for w in range(width):
                    img[h*100:(h+1)*100,w*100:(w+1)*100,:]=dview[i][h][w]
                    v = round(data[i][h][w],5)
                    cv2.putText(img,str(v),(w*100,h*100+60),1,1,(0,0,255))
            savepath = savedir+"/"+str(i)+".jpg"
            cv2.imwrite(savepath,img*255)
    elif len(shape) == 2:
        prod = shape[0]*shape[1]
        num = int(math.ceil(prod/400))
        for i in tqdm(range(min(num,10))):
            remain = min(1000, int((prod-i*400)/8*20))
            img = np.zeros((remain,800,3),dtype=np.float32)
            for j in range(50):
                for k in range(8):
                    index = i*400+j*8+k
                    if index >= prod:
                        break
                    sx = index%shape[1]
                    sy = int(index/shape[1])
                    img[j*20:(j+1)*20,k*100:(k+1)*100,:] = dview[sy][sx]
                    v = data[sy][sx]
                    cv2.putText(img,str(v),(k*100,j*20+15),1,1,(0,0,255))
            savepath = savedir+"/"+str(i)+".jpg"
            cv2.imwrite(savepath,img*255)

if __name__=="__main__": 
    prototxt = "deploy.prototxt"
    caffemodel = "deploy.caffemodel"
    if len(sys.argv) > 1:
        prototxt = sys.argv[1]
    if len(sys.argv) > 1:
        caffemodel = sys.argv[2]
    net = caffe.Net(prototxt, caffemodel, caffe.TEST)
 
    for item in net.params.items():
        name, layer = item
        data = layer[0].data
        print(name, data.shape)
        layer_type = net.layer_dict[name].type
        if layer_type == "BatchNorm" or layer_type=="Scale":
            continue
        draw_filters(name, data)