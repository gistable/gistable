"""
   Search and replace recursive 
   Usage:
        ~$ python replace.py [rootdir] [searched_text] [replace_text]
"""

import os
import sys

if len(sys.argv) <= 1:
    print "Debe seleccionarse el directorio de raiz"
    exit()

if len(sys.argv) <= 2:
    print "Debe especificarse que buscar"
    exit()

if len(sys.argv) <= 3:
    print "Debe especificarse con que reemplazar"
    exit()

root = sys.argv[1]
find = sys.argv[2]
replacement = sys.argv[3]

for root, subfolder, files in os.walk(root):

    for file in files:

        path = os.path.join(root, file)

        if not '.git' in file and not '.git' in root:
            print path
            try:
                f = open(path, 'r')
                c = f.read()
                f.close()

                f = open(path, 'w')
                c = c.replace(find, replacement)
                f.write(c)
                f.close()

            except Exception, e:
                print e
