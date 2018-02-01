# Name: EXIFmover.py
# Author: Brian Klug (@nerdtalker / brian@brianklug.org)

# Purpose:
# Move Files into directory based on EXIF data make and model
# Designed to un-clusterfuck the Dropbox camera upload directory which is a mess of every
# JPEG and PNG ever if you use it like I do on a bunch of phones, and thus totally unwieldy
# and full of images sorted by date or else nothing sometimes, dropbox seems nondeterminstic

# Moves files into /[Image Make]+[Image Model]/ eg /Camera Uploads/LGE Nexus 4/
# Creates directory if it doesn't exist, moves into that directory if it exists
# Files without EXIF get moved into /nomake nomodel (EG screenshots / nonsense) except exifmover/exif.py
# This is experimental and one-way in a destructive sense, I take no responsibility
# if this absolutely destroys your directory structure for some reason

# I STRONGLY recommend making a copy of Camera Uploads, then running this on the copy, first

# Requires EXIF-PY to be installed and importable
# EXIF-PY can be obtained from https://github.com/ianare/exif-py 
# Previous implementation used EXIF.py standalone, updated to work with installable version

# Run simply (eg from ipython "run exifmover.py" inside "Camera Upload")

# Tested on OS 10.8.2 and Python 2.7.3 EPD
# Tested on Windows XP and Python 2.7.3 EPD
# Tested on Ubuntu 11.10

try: 
    import exifread
except:
    print "exifread was not found in the same directory as exifmover.py"
import os
import time

start_time=time.time()

path = os.getcwd()
dirList=os.listdir(path)
excludedfiles = ["EXIF.py","EXIFmover.py","exifmover.py","thumbs.db",".DS_Store","EXIF.pyc"]

for fname in dirList:
    if os.path.isfile(fname):
        if fname not in excludedfiles:
            print "File name is " + fname
            f = open(fname)
            try:
                tags = exifread.process_file(f)
            except:
                print "Couldn't read tag on " + fname
            try: 
                make = tags['Image Make'].printable 
            except: make = 'nomake'
            try: 
                model = tags['Image Model'].printable 
            except: model = 'nomodel'
            src = path + "/" + fname
            #print "source is " + src
            dst = path + "/" + make + " " + model + "/"
            #print "destination is " + dst
            if os.path.isdir(dst) == False: 
                os.mkdir(dst)
            
            #print "made" + dst
            destination = dst+fname
            f.close()
            try: 
                os.rename(src,destination)
            except: 
               print "Oh noes. That didn't work for some reason"

print 'Done. Execution took {:0.3f} seconds'.format((time.time() - start_time))
