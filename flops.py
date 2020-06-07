import os
import sys
import cv2

frameworks = [["prototxt","caffemodel"],["onnx"],["pb"],["pbtxt"],["cfg","weights"]]

def get_possible_file(modelpath):
    modelname, ext = os.path.splitext(modelpath)
    for fw in frameworks:
        if ext[1:] == fw[0]:
            if len(fw) > 1:
                return modelname+"."+fw[0], modelname+"."+fw[1]
            else:
                return modelpath
    for fw in frameworks:
        model = modelname + "."+ fw[0]
        if os.path.exists(model):
            if len(fw) > 1:
                config = modelname + "."+ fw[1]
                if os.path.exists(config):
                    return model, config
            else:
                return model

def get_flops(net, shape = (1,3,128,128), verbose = True):
    layerNames = net.getLayerNames()
    infos = []
    maxnamelen = 8
    for layerName in layerNames:
        layerId = net.getLayerId(layerName)
        layer = net.getLayer(layerId)
        flop = net.getFLOPS(layerId, shape)
        if flop > 0:
            maxnamelen = len(layerName) if len(layerName) > maxnamelen else maxnamelen
            blobs = layer.blobs
            info = {}
            info['name'] = layerName
            info['id'] = layerId
            info['flops'] = flop
            if len(blobs) > 0:
                param = blobs[0].size
                if len(blobs) > 1:
                    param += blobs[1].size
                info['filter_shape'] = blobs[0].shape
                info['params'] = param
            else:
                info['filter_shape'] = 0
                info['params'] = 0
            infos.append(info)
    flops = net.getFLOPS(shape)
    if verbose:
        print('layerId','layerName'.ljust(maxnamelen+1), 'filter Shape'.ljust(16),'Params'.ljust(8), 'FLOPs'.ljust(12), "Ratio")
        for info in infos:
            ratio = round(info['flops']*100.0/flops,3)
            print(str(info['id']).ljust(8),info['name'].ljust(maxnamelen+1),str(info['filter_shape']).ljust(16),str(info['params']).ljust(8),str(info['flops']).ljust(12),str(ratio)+"%")
    memory = net.getMemoryConsumption(shape)
    return flops, memory

if __name__ == "__main__":
    modelpath = "deploy.prototxt"
    if len(sys.argv) > 1:
        modelpath = sys.argv[1]
    model = get_possible_file(modelpath)
    if model is None:
        print("no model named "+modelpath)
        exit(0)
    if type(model) == tuple:
        net = cv2.dnn.readNet(model[0], model[1])
    else:
        net = cv2.dnn.readNet(model)
    flops, memory = get_flops(net)
    print(model, flops, memory)