cmake_minimum_required(VERSION 3.14)
project(solar_simulation)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add Pybind11 subdirectory
add_subdirectory(pybind11)

# Create the Pybind11 module
pybind11_add_module(adjust_pv_module adjust_pv.cpp adjust_pv_bindings.cpp)

# (Optional) If you have additional include directories or libraries, add them here
# target_include_directories(adjust_pv_module PRIVATE /path/to/other/includes)
# target_link_libraries(adjust_pv_module PRIVATE some_other_library)