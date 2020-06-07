import sys
import cv2
import caffe
import numpy as np
np.set_printoptions(precision=6, suppress=True)

def showlayerinfo(f, name, data):
    print(name, data.shape)
    f.write(name+str(data.shape)+"\n")
    f.write(str(data)+"\n")

def print_weights(net):
    conv_layers = ['Convolution','Scale','DepthwiseConvolution','Deconvolution','InnerProduct']
    with open("weights.txt","w") as f:
        for name in net.params:
            layer_type = net.layer_dict[name].type
            if layer_type in conv_layers:
                parameter = net.params[name]
                weight = parameter[0].data.squeeze()
                showlayerinfo(f, name+"_weight:", weight)
                if len(parameter) > 1:
                    bias = parameter[1].data.squeeze()
                    showlayerinfo(f, name+"_bias:", bias)
            elif layer_type == 'BatchNorm':
                parameter = net.params[name]
                mean = parameter[0].data.squeeze()
                var = parameter[1].data.squeeze()
                showlayerinfo(f, name+"_mean:", mean)
                showlayerinfo(f, name+"_var:", var)
            else:
                print(name, layer_type+ "not supported")

def get_features(net, img = None, features = None):
    shape = net.blobs[net.inputs[0]].data.shape
    if img is None:
        inp = np.ones(shape)
    else:
        img = cv2.resize(img, shape[2:])
        img = img.astype(np.float32)
        img -= (103.94, 116.78, 123.68)
        inp = img.transpose(2, 0, 1)
    net.blobs[net.inputs[0]].data[...] = inp
    outputs = net.forward()
    with open("caffe_featrues.txt","w") as f:
        if features is None:
            features = net.blobs
        for feature in features:
            data = net.blobs[feature].data
            print(feature, data.shape)
            f.write(feature+" "+str(data.shape)+"\n")
            f.write(str(data)+"\n")
    with open("caffe_outputs.txt","w") as f:
        for out in net.outputs:
            data = outputs[out]
            f.write(out+" "+str(data.shape)+"\n")
            f.write(str(data)+"\n")

if __name__=="__main__":
    net_file = "deploy.prototxt"
    caffe_model = "deploy.caffemodel"
    if len(sys.argv) == 2:
        name = sys.argv[1]
        net_file = name + ".prototxt"
        caffe_model = name + ".caffemodel"
    elif len(sys.argv) == 3:
        net_file = sys.argv[1] + ".prototxt"
        caffe_model = sys.argv[2] + ".prototxt"
    net = caffe.Net(net_file, caffe_model, caffe.TEST)
    if len(sys.argv) == 4:
        imgpath = sys.argv[3]
        img = cv2.imread(imgpath)
        if img is None:
            print("cannot read "+imgpath)
        get_features(net, img)
    else:
        print_weights(net)