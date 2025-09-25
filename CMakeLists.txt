cmake_minimum_required(VERSION 3.14)
project(maze_generator LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG v2.11.1   # stable tag; change if you want a different version
)
# Fetch and make pybind11 available as an imported target
FetchContent_MakeAvailable(pybind11)

# Allow user to override Python executable if desired:
if(NOT DEFINED Python_EXECUTABLE)
  find_package(Python COMPONENTS Interpreter REQUIRED) # we only need interpreter to register python executable
endif()

# Create module
pybind11_add_module(maze_generator maze_generator.cpp)
target_compile_features(maze_generator PUBLIC cxx_std_17)