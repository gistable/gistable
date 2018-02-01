#!/usr/local/bin/python

# Tested on Mac OS Yosemite circa July 2015, when NNVL had just started
# making Himawari images available. Hopefully they keep it up!
# Installation:
#   pip install appscript
#   change the image storage path below
#   make executable (chmod +x himawari_bg.py)
#   setup a cron job to run this script every 10 minutes

#import os
import ftplib
import datetime
import appscript
import subprocess

# set this to your preferred image location.
path = "/users/scott/Pictures/Desktop Backgrounds/himawari"

img = "%s/himawari.jpg" % (path)

ftp = ftplib.FTP("ftp.nnvl.noaa.gov")
ftp.login()
ftp.cwd("GOES/HIMAWARI")
fn = sorted(ftp.nlst())[-1]  # files are sensibly named w/ timestamps

# for debugging purposes...
#with open(path + "/ts.txt", 'w') as f:
#    f.write(str(datetime.datetime.now()))

with open(img, 'wb') as fh:
    ftp.retrbinary('RETR ' + fn, fh.write)

# change all display backgrounds; doesn't work on other spaces.
se = appscript.app('System Events')
desktops = se.desktops.display_name.get()
for d in desktops:
    desk = se.desktops[appscript.its.display_name == d]
    desk.picture.set(appscript.mactypes.File(img))

# this is the only way I could reliably convince osx to refresh and not use
# some magically cached versions sometimes. afaict there are no adverse
# effects of killing the dock every 10 minutes
subprocess.call(['/usr/bin/killall', 'Dock'])