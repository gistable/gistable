#!/usr/bin/env python

"""
Extract malware from Contagio Zip files, determining the password
automatically.

Note that the password for each zip file consists of a common base password
along with the last character of the file name (prior to the .zip extension).
If you don't know the base password, please contact Mila directly.

Files can be downloaded from http://contagiodump.blogspot.com/

@author: Greg Back

Requires 7zip
"""


import os
import shlex
import shutil
import subprocess
import sys

BASE_PW = "<FILL THIS IN>"
OLD_PW = "<FILL THIS IN TOO>"

def main():
    for f in sys.argv[1:]:
        (basename, _) = os.path.splitext(os.path.basename(f))

        lastchar = basename[-1]

        outdir = basename
        os.mkdir(outdir)

        # Unzip the zipfile of malware into a new directory named after the                                  
        # base name of the original zip file                                                                 
        cmd = shlex.split('7z x {0} -p{1}{2} -o{3}'.format(f, BASE_PW, lastchar, outdir))
        # notice the -y. Will overwrite files if it has to use the old password
        oldcmd = shlex.split('7z x {0} -p{1} -o{2} -y'.format(f, OLD_PW, outdir))

        if subprocess.call(cmd) != 0:
            # if it fails, try with old password
            shutil.rmtree(outdir) # nice thought but doesn't work...
            subprocess.call(oldcmd)

        # delete the output directory if nothing was extracted                                               
        if not os.listdir(outdir):
            os.rmdir(outdir)


if __name__ == '__main__':
    main()
