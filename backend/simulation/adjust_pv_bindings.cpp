// adjust_pv_bindings.cpp

#include "adjust_pv.h"
#include <pybind11/pybind11.h>

namespace py = pybind11;

// Binding function for adjust_pv_estimate with multiplier, azimuth, and tilt
void bind_adjust_pv_estimate(py::module &m) {
    m.def("adjust_pv_estimate", &adjust_pv_estimate, 
          "Adjust PV estimate based on input value, multiplier, azimuth, and tilt",
          py::arg("input"), py::arg("multiplier"), py::arg("azimuth"), py::arg("tilt"));
}

// Module definition
PYBIND11_MODULE(adjust_pv_module, m) {
    m.doc() = "Module for adjusting PV estimates with multiplier, azimuth, and tilt";
    bind_adjust_pv_estimate(m);
}