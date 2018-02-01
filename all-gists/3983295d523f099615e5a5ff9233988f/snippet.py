# -*- encoding= utf-8
“”“

“””
import os
import sys
import re
import shutil
import time
from collections import defaultdict


dir_pattern = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')

def move_files(files, folder):
    """
    move files into specified folder
    """
    if not os.path.exists(folder):
        os.mkdir(folder)
    for file in files:
        shutil.move(file,os.path.join(folder, file))


def files_in_folder(folder):
    for filename in os.listdir(folder):
        yield filename, time.strftime('%Y-%m-%d', time.localtime(os.path.getatime(filename)))



def main(working_directory):
    os.chdir(working_directory)

    file_dict = defaultdict(list)

    for file, atime in files_in_folder(os.path.abspath('.')):
        if not (os.path.isdir(file) and dir_pattern.match(file)):
            file_dict[atime].append(file)

    for folder, files in file_dict.items():
        move_files(files, str(folder))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        working_directory = os.path.abspath(sys.argv[1])
    else:
        working_directory = os.path.abspath(os.path.join(os.environ['home'],'Downloads'))
    main(working_directory)
