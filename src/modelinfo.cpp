#include "modelinfo.h"
#include "caffe/caffe.hpp"

int modelinfo(std::string modelname){
    caffe::NetParameter proto;
    std::string modelpath = modelname + ".caffemodel";
    caffe::ReadProtoFromBinaryFile(modelpath, &proto);
    std::cout<<"Parsing "<<modelpath<<std::endl;
    caffe::WriteProtoToTextFile(proto, modelname + ".txt");
    return 0;
}