#!/usr/bin/env python
# encoding: utf-8

import os
import shlex
import subprocess
import optparse

GNP_TEMPLATE="""
set term png size 800,600
set out "{0}.png"

set title "{0}"

set xlabel "{1}"
set ylabel "{2}"

plot "{0}" u {3}:{4} w l

"""

valid_extensions = [".txt", ".dat"]

def do(string, desc=""):
    """ execute a string as a shell call """
    if len(desc) > 0: print(desc) 

    cmd = shlex.split(string)
    subprocess.call(cmd)     

def get_files(startpath='.'):
    for root, dirs, files in os.walk(startpath):
        for name in files:
            filename = os.path.join(root,name)
            yield filename             


def make_image(f):
    with open(gnp_temp_file, "w") as gnp:
        file_contents = GNP_TEMPLATE.format(f, args.x_label, args.y_label, args.x_col, args.y_col)
        gnp.write(file_contents)
    
    do("gnuplot " + gnp_temp_file)

    do("rm " + gnp_temp_file)

def valid_file(f):
    extension = os.path.splitext(f)[-1]
    if extension in valid_extensions:
        return True
    
    return False

parser = optparse.OptionParser(description="Plots x,y data files in a folder as pngs")
parser.add_option('-f', action='store', dest='input_folder', help='target input folder')
parser.add_option('-x', action='store', dest='x_label', help='X axis label (default = x)', default='x')
parser.add_option('-y', action='store', dest='y_label', help='y axis label (default = y)', default='y')
parser.add_option('--xcol', action='store', dest='x_col', help='X axis column number (default = 1)', default='1')
parser.add_option('--ycol', action='store', dest='y_col', help='y axis column number (default = 2)', default='2')

(args, extras) = parser.parse_args()

gnp_temp_file = args.input_folder + "/temp.gnp" 

if __name__ == '__main__':
    for fname in get_files(args.input_folder):
        if valid_file(fname):
            print fname
            make_image(fname)
