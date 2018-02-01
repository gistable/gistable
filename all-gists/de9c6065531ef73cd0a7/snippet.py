__author__ = 'Raúl Sampedro'
import os
import re
import sys
from os.path import join


def find(path, regexp, map_func):
    for pwd, dirs, files in os.walk(path):
        for file in files:
            if re.match(regexp, file, re.IGNORECASE):
                map_func(join(pwd,file))

def renameUnderScore(file):
    print("Renaming:",file)
    os.rename(file, file + "_")

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print("Usage: %s dir_path" % sys.argv[0])
        exit(1)
    else:
        find(sys.argv[1], r'.*\.(exe|com|bat|dll)$', renameUnderScore)