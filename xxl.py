import cv2
import numpy as np
import random
COLORS=[[0,255,0],[255,0,0],[0,0,255],[255,0,255],[0,255,255]]
size = 60
pad = 5
stride = size + 2 * pad

def fill_rect(img, i, j, color):
    x1 = j * stride + pad
    y1 = i * stride + pad
    x2 = (j+1)*stride - pad
    y2 = (i+1)*stride - pad
    cv2.rectangle(img,(x1,y1),(x2,y2),color,-1)
def fill_circle(img, i, j,color):
    x = j * stride + stride // 2
    y = i * stride + stride //2
    cv2.circle(img, (x,y), size//2, color,-1)
def fill_triangle(img, i, j ,color):
    x1 = j * stride + stride // 2
    y1 = i * stride + pad
    x2 = (j+1)*stride - pad
    y2 = (i+1)*stride - pad
    x3 =  j*stride + pad
    y3 = (i+1)*stride - pad
    pts = []
    pts.append((x1,y1))
    pts.append((x2,y2))
    pts.append((x3,y3))
    pts = np.array(pts)
    cv2.fillPoly(img,[pts],color,size//2)
def fill_triangle2(img, i, j ,color):
    x1 = j * stride + pad
    y1 = i * stride + pad
    x2 = (j+1)*stride - pad
    y2 = i*stride + pad
    x3 =  j*stride + stride//2
    y3 = (i+1)*stride - pad
    pts = []
    pts.append((x1,y1))
    pts.append((x2,y2))
    pts.append((x3,y3))
    pts = np.array(pts)
    cv2.fillPoly(img,[pts],color,size//2)

def generate_grid(img, i, j):
    x1 = j * stride
    y1 = i * stride
    x2 = (j+1)*stride
    y2 = (i+1)*stride
    cv2.rectangle(img,(x1,y1),(x2,y2),(255,255,255),2)

def fill_grid(img, i, j, color, num):
    if num == 0:
        fill_circle(img, i, j, color)
    elif num == 1:
        fill_rect(img, i, j, color)
    elif num == 2:
        fill_triangle(img, i, j, color)
    elif num == 3:
        fill_triangle2(img, i, j, color)
    else:
        fill_triangle(img, i, j, color)

def hasline(grids):
    sts = np.zeros((grids.shape[0],grids.shape[1]),dtype=np.int)
    # for i in range(grids.shape[0]):
    #     sts[i,0] = 1
    sts = np.ones(grids.shape[0],dtype = np.int)
    max_length = 1
    for i in range(grids.shape[0]):
        for j in range(1, grids.shape[1]):
            if grids[i][j] == grids[i][j-1]:
                sts[i] = sts[i]+1
                if sts[i] > max_length:
                    max_length = sts[i]
            else:
                sts[i] = 1
    if max_length >= 3:
        return False
    max_length = 1
    sts = np.ones(grids.shape[1],dtype = np.int)
    for j in range(grids.shape[1]):
        for i in range(1,grids.shape[0]):
            if grids[i][j] == grids[i-1][j]:
                sts[j] = sts[j]+1
                if sts[j] > max_length:
                    max_length = sts[j]
            else:
                sts[j] = 1
    if max_length >= 3:
        return False
    return True

def print_grid(grids):
    for i in range(grids.shape[0]):
        line = "["
        for j in range(grids.shape[1]):
            line = line +str(grids[i][j])+", "
        line = line+"],"
        print(line)

def draw_grid(grids):
    img = np.ones((490,490,3),dtype=np.uint8)*255
    img[:,:,2] = 0
    for i in range(grids.shape[0]):
        for j in range(grids.shape[1]):
            color = COLORS[grids[i][j]]
            generate_grid(img, i, j)
            fill_grid(img, i, j, color, grids[i][j])
            #fill_triangle2(img, i, j, color)
    return img

def swap(grids,p1=(0,3),p2=(0,4)):
    grids[p1], grids[p2] = grids[p2], grids[p1]

    pass

def generate_map(rows=7,cols=7):
    # grids = np.random.random_integers(5, size=(rows,cols)) - 1
    grids = np.array([  
            [1, 4, 1, 2, 4, 3, 2, ],
            [0, 4, 1, 2, 2, 0, 3, ],
            [2, 3, 0, 0, 2, 1, 2, ],
            [4, 4, 3, 4, 0, 2, 1, ],
            [2, 3, 2, 1, 2, 3, 3, ],
            [1, 1, 0, 2, 1, 2, 4, ],
            [0, 4, 0, 4, 4, 3, 0, ],
        ],dtype = np.int)
    valid = hasline(grids)                
    while not valid:
        grids = np.random.random_integers(5, size=(rows,cols)) - 1
        valid = hasline(grids)
    print_grid(grids)
    img = draw_grid(grids)
    cv2.imwrite("xxl.jpg", img)
    swap(grids)
    img2 = draw_grid(grids)
    cv2.imwrite("xxl2.jpg", img2)
    cv2.imshow("img", img)
    cv2.waitKey()

if __name__=="__main__":
    generate_map()