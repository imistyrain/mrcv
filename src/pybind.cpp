#include "modelinfo.h"
#include <pybind11/pybind11.h>
namespace py = pybind11;

PYBIND11_MODULE(modelinfo, m){
    m.doc() = "modelinfo";
    m.def("export", &modelinfo, "export model weights", py::arg("modelname")=1);
}