#grabFrame.py:

#!/usr/bin/env python
import time
import sys
import cv
import cv2


cam = cv2.VideoCapture(-1)
cam.set(cv.CV_CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 488)


while True:
    time.sleep(1.0/15.0)
    s, imgArray = cam.read()
    image = cv.fromarray(imgArray)
    sys.stdout.write(image.tostring())


#stream with:
./grabFrame.py | ffmpeg -f rawvideo -r 15 -s 640x488 -pix_fmt bgr24 -i - -f flv -r 15 -s 640x480 "rtmp://live.justin.tv/app/$(cat ~/.twitch_key)"