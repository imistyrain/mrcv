import sys
import caffe
from numpy import prod, sum

def get_flops(deploy_file, show_detail=True,flop_layers = ['Convolution', 'DepthwiseConvolution', 'InnerProduct']):
    net=caffe.Net(deploy_file,caffe.TEST)
    params=0
    flops=0
    infos=[]
    print(deploy_file)
    maxnamelen = 8
    for item in net.params.items():
        name, layer = item
        layer_type = net.layer_dict[name].type
        if layer_type in flop_layers:
            maxnamelen =len(name) if len(name) > maxnamelen else maxnamelen
            param = layer[0].count# + layer[1].count
            #bm = net.blobs[net.bottom_names[name][0]]
            bt = net.blobs[net.top_names[name][0]]
            flop = param*bt.width*bt.height
            if show_detail:
                info={}
                info['name']=name
                info['filter_shape']=layer[0].data.shape
                info['out_shape']=bt.data.shape
                info['params']=param
                info['flops']=flop
                infos.append(info)
            params += param
            flops += flop
    if show_detail:
        print('layer name'.ljust(maxnamelen+1), 'Filter Shape'.ljust(16),'Output Size'.ljust(16), 'Params'.ljust(8), 'Flops'.ljust(12),"Ratio")
        for info in infos:
            ratio = round(info['flops']*100.0/flops,3)
            print(info['name'].ljust(maxnamelen+1),str(info['filter_shape']).ljust(16),
            str(info['out_shape']).ljust(16),str(info['params']).ljust(8),str(info['flops']).ljust(12),str(ratio)+"%")
    print ('Layers num: ' + str(len(net.params.items())))
    print("Total number of parameters: ",params)
    print("Total number of FLOPs: ",flops)
    return params, flops

if __name__ == '__main__':
    deploy_file="deploy.prototxt"
    if len(sys.argv) > 1:
        deploy_file = sys.argv[1]
    get_flops(deploy_file)