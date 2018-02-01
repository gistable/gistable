"""
Run this python script in the root directory of an Juce project that has been created by the Introjucer

usage:
>cd into/directory/where/jucerfileis/
>curl https://gist.githubusercontent.com/alexgustafson/4df824c0654056e18b9e/raw/b92517296c6d7d1af9b1c71bfffe564b4838da70/pycmakejuce.py > pycmakejuce.py
>python pycmakejuce.py
"""

import xml.etree.ElementTree as ET
import glob
import subprocess
import os

BUILD_DIR = "./Builds"
CMAKE_JUCE_DIR = BUILD_DIR + "/CMakeJuce"
REPO = "https://github.com/teragonaudio/CMakeJuce.git"


# list all first level sub directories in a given path (dir_path)
def get_subdirectories(dir_path):
    return [os.path.join(dir_path, x) for x in os.listdir(dir_path)]

# perform git commands
def git(*args):
    return subprocess.check_call(['git'] + list(args))

# clone a repository into a target directory
def clone_cmakejuce_from_github(repo, target_dir):
    git("clone", repo, target_dir)


def write_string_to_file(filename, string):
    if os.path.exists(filename):
        print("The file {0} already exists".format(filename))
    else:
        text_file = open(filename, 'w')
        text_file.write(string)
        text_file.close()

try:
    jucer_filename = glob.glob('./*.jucer')[0]
    tree = ET.parse(jucer_filename)
    root = tree.getroot()
except:
    print("This does not appear to be the root directory of an Introjucer project")

project_name = root.attrib['name']
jucer_version = root.attrib['jucerVersion']

build_directories = get_subdirectories('./Builds')

if CMAKE_JUCE_DIR not in build_directories:
    clone_cmakejuce_from_github(REPO, CMAKE_JUCE_DIR)


project_cmakelists = """
cmake_minimum_required(VERSION 2.8)
project(%(project_name)s)

if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    add_subdirectory(Builds/MacOSX)
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    add_subdirectory(Builds/Linux)
endif()""" % {"project_name": project_name}

build_cmakelists = """
cmake_minimum_required(VERSION 2.8)
include(../CMakeJuce/juce.cmake)
"""


write_string_to_file("CMakeLists.txt", project_cmakelists)

for dir in build_directories:
    write_string_to_file(os.path.join(dir, "CMakeLists.txt"), build_cmakelists)