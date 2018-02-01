#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import shutil
from urllib import request
import zipfile

def replace_css(file, css):
    zin = zipfile.ZipFile(file)
    new_file = file.replace('.epub', '_new.epub')
    zout = zipfile.ZipFile(new_file, 'w')
    for item in zin.infolist():
        buffer = zin.read(item.filename)
        if (item.filename == 'OEBPS/readlist_epub.css'):
            zout.writestr(item, css)
        else:
            zout.writestr(item, buffer)
    zout.close()
    zin.close()
    
    shutil.move(new_file, file)
    

# https://gist.github.com/imginohu/5890070
css_url = 'https://gist.github.com/imginohu/5890070/raw/54ded069f3f172751225b27f31216ed635e2d49b/readlist_epub.css'

CSSSTR = request.urlopen(css_url).read()

parser = argparse.ArgumentParser(
    description='replace readability default css for better nook simple touch reading')
parser.add_argument(dest='filenames',metavar='filename', nargs='*')
args = parser.parse_args()

filenames = [f for f in args.filenames 
               if zipfile.is_zipfile(f) and f.endswith('epub')]

for file in filenames:
    replace_css(file, CSSSTR)
    print(file, 'is processed.')