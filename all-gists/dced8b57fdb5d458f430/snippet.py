"""

This python script encodes all files in specified working directory.
Sources: http://ffmpeg.org/trac/ffmpeg/wiki/x264EncodingGuide

command: python video-encode.py /dir/to/encode
 output: /dir/to/encode/encoded

"""

from os import path, listdir, makedirs
from subprocess import call
import sys
import shutil

# -------------------------------------------------------------------------------
# CONFIGURABLE SETTINGS
# -------------------------------------------------------------------------------

# output video dimensions
DIMENSIONS = '1920x1080'
# output video framerate
FRAMERATE = '30'
# controls the approximate bitrate of the encode
BITRATE = '6M'
# encoding speed:compression ratio
PRESET = 'veryslow'
# output file format
OUTPUT_FILE_EXTENSION = 'mp4'
# relative output directory
RELATIVE_OUTPUT_DIRECTORY = 'encoded'
# ffmpeg path
FFMPEG_PATH = '/usr/bin/ffmpeg'

# -------------------------------------------------------------------------------
# FUNCTIONS
# -------------------------------------------------------------------------------


# example : ffmpeg -i i.mp4 -f mp4 -s 1920x1080 -b 6000k -r 30 -vcodec libx264 -preset veryslow -threads auto o.mp4
def encode_file(input_file_path, output_directory):

    output_file_path = output_directory + compile_output_file_name(input_file_path)
    call([
        FFMPEG_PATH,
        '-i', input_file_path,
        '-f', OUTPUT_FILE_EXTENSION,
        '-s', DIMENSIONS,
        '-b:v', BITRATE,
        '-r', FRAMERATE,
        '-vcodec', 'libx264',
        '-preset', PRESET,
        '-threads', '0',
        '-strict', 'experimental',
        output_file_path
    ])


def compile_output_file_name(input_file_path):

    input_file_name = path.basename(input_file_path)
    input_file_name_without_extension = path.splitext(input_file_name)[0]  # split ext, not split text.
    return input_file_name_without_extension + '.' + OUTPUT_FILE_EXTENSION


def clean_directory(dir_path):
    shutil.rmtree(dir_path, ignore_errors=True)
    makedirs(dir_path)


# -------------------------------------------------------------------------------
# SCRIPT
# -------------------------------------------------------------------------------
if len(sys.argv) < 2:
    print('please, provide directory to encode')
    exit(1)

inputDirectory = path.join(sys.argv[1], '')  # to check if it ends in a /, and if not add the / to it.
outputDirectory = path.join(inputDirectory, RELATIVE_OUTPUT_DIRECTORY, '')

clean_directory(outputDirectory)
filesInInputDirectory = [inputDirectory + fileName for fileName in listdir(inputDirectory)];
filesToEncode = filter(path.isfile, filesInInputDirectory)  # exclude folders

for file in filesToEncode:
    encode_file(file, outputDirectory)
