# This script takes a video's individual frames and overlays them to produce a composite "long exposure" image.
#
# Usage: python expose.py video.mp4 width height
#
# IMPORTANT: you'll need to edit this script to set the value of 'alpha' appropriate for your video's length and desired brightness.

from __future__ import division
import subprocess as sp
import numpy
from PIL import Image, ImageDraw
import re
import time
import sys

# Alpha is the opacity of each frame. I've had success with values of 5/n to 36/n, where n
# is the number of frames in your video. You'll have to experiment. Sample values:
# 72 frame video: 0.069 (5/72)
# 12286 frame video: 0.0003 (36/12286)
alpha = 0.01
print("Default value for alpha: {}".format(alpha))

# Command you use to launch ffmpeg. In Windows you might need to use FFMPEG_BIN="ffmpeg.exe"; Linux/OSX should be OK.
FFMPEG_BIN = "ffmpeg"

# Timestamp so you can see how long it took
start_time = "Script started at " + time.strftime("%H:%M:%S")
print(start_time)

# optional starting time hh:mm:ss.ff; default value set to 00:00:00.0
hh = "%02d" % (0,)
mm = ":%02d" % (0,)
ss = ":%02d" % (0,)
ff = ".0"
print "Timestamp for first frame: "+hh+mm+ss+ff

# input file (first argument)
filename = str(sys.argv[1])
width = int(sys.argv[2])
height = int(sys.argv[3])
# output image file (same as input file, with non-alphanums stripped):
outfilename = re.sub(r'\W+', '', filename) + ".png"
print("Filename: {}".format(filename))
print("Dimensions: {},{}".format(width,height))

###
### This section: credit to http://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/

# Open the video file. 
command = [ FFMPEG_BIN,
            '-threads', '4',
            '-ss', hh+mm+ss,
            '-i', filename,
            '-f', 'image2pipe',
            # '-filter:v', 'setpts=PTS/8', # optional; take every 8th frame; offers some performance improvement
            '-pix_fmt', 'rgb24',
            '-vcodec', 'rawvideo', '-']
pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

# create a numpy array from the first video frame; we'll add subsequent frames on top
frame = numpy.fromstring(pipe.stdout.read(width*height*3), dtype='uint8').reshape((height,width,3)) * alpha

# x is optional; you might want to use it to break the 'while' loop in testing
x=0
# stack more frames on top
while pipe.stdout.read(width*height*3):
    try:
        # read the next frame from the pipe
        nextframe = numpy.fromstring(pipe.stdout.read(width*height*3), dtype='uint8').reshape((height,width,3)) * alpha
        # add the current frame to the composite frame; doing it this way prevents 8-bit values rolling over from 255 to 0
        # (from http://stackoverflow.com/questions/29611185/avoid-overflow-when-adding-numpy-arrays)
        nextframe = 255 - nextframe
        numpy.putmask(frame, nextframe < frame, nextframe)
        frame += 255 - nextframe    
    except:
        print("No more frames to process (or error occurred). Number of frames processed:", x)
    x += 1
    
frame = frame.astype('uint8') # convert frame pixel values to correct dtype before saving
im = Image.fromarray(frame)
im.save("output.png")

print(start_time)
print("Script finished at {}".format(time.strftime("%H:%M:%S")))
print("Total frames processed: {}".format(x))