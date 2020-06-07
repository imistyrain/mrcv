#include "modelinfo.h"

int main(int argc, char *argv[]) {
    std::string modelname = "deploy";
    if (argc > 1){
        modelname = argv[1];
    }
    modelinfo(modelname);
    return 0;
}