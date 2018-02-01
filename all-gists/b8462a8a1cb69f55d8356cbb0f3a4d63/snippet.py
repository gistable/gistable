# Fast reading from the raspberry camera with Python, Numpy, and OpenCV
# Allows to process grayscale video up to 124 FPS (tested in Raspberry Zero Wifi with V2.1 camera)
#
# Made by @CarlosGS in May 2017
# Club de Robotica - Universidad Autonoma de Madrid
# http://crm.ii.uam.es/
# License: Public Domain, attribution appreciated

import cv2
import numpy as np
import subprocess as sp
import time
import atexit

frames = [] # stores the video sequence for the demo
max_frames = 300

N_frames = 0

# Video capture parameters
(w,h) = (640,240)
bytesPerFrame = w * h
fps = 250 # setting to 250 will request the maximum framerate possible

# "raspividyuv" is the command that provides camera frames in YUV format
#  "--output -" specifies stdout as the output
#  "--timeout 0" specifies continuous video
#  "--luma" discards chroma channels, only luminance is sent through the pipeline
# see "raspividyuv --help" for more information on the parameters
videoCmd = "raspividyuv -w "+str(w)+" -h "+str(h)+" --output - --timeout 0 --framerate "+str(fps)+" --luma --nopreview"
videoCmd = videoCmd.split() # Popen requires that each parameter is a separate string

cameraProcess = sp.Popen(videoCmd, stdout=sp.PIPE) # start the camera
atexit.register(cameraProcess.terminate) # this closes the camera process in case the python scripts exits unexpectedly

# wait for the first frame and discard it (only done to measure time more accurately)
rawStream = cameraProcess.stdout.read(bytesPerFrame)

print("Recording...")

start_time = time.time()

while True:
    cameraProcess.stdout.flush() # discard any frames that we were not able to process in time
    # Parse the raw stream into a numpy array
    frame = np.fromfile(cameraProcess.stdout, count=bytesPerFrame, dtype=np.uint8)
    if frame.size != bytesPerFrame:
        print("Error: Camera stream closed unexpectedly")
        break
    frame.shape = (h,w) # set the correct dimensions for the numpy array

    # The frame can be processed here using any function in the OpenCV library.

    # Full image processing will slow down the pipeline, so the requested FPS should be set accordingly.
    #frame = cv2.Canny(frame, 50,150)
    # For instance, in this example you can enable the Canny edge function above.
    # You will see that the frame rate drops to ~35fps and video playback is erratic.
    # If you then set fps = 30 at the beginning of the script, there will be enough cycle time between frames to provide accurate video.
    
    # One optimization could be to work with a decimated (downscaled) version of the image: deci = frame[::2, ::2]
    
    frames.append(frame) # save the frame (for the demo)
    #del frame # free the allocated memory
    N_frames += 1
    if N_frames > max_frames: break

end_time = time.time()

cameraProcess.terminate() # stop the camera


elapsed_seconds = end_time-start_time
print("Done! Result: "+str(N_frames/elapsed_seconds)+" fps")


print("Writing frames to disk...")
out = cv2.VideoWriter("slow_motion.avi", cv2.cv.CV_FOURCC(*"MJPG"), 30, (w,h))
for n in range(N_frames):
    #cv2.imwrite("frame"+str(n)+".png", frames[n]) # save frame as a PNG image
    frame_rgb = cv2.cvtColor(frames[n],cv2.COLOR_GRAY2RGB) # video codec requires RGB image
    out.write(frame_rgb)
out.release()

print("Display frames with OpenCV...")
for frame in frames:
    cv2.imshow("Slow Motion", frame)
    cv2.waitKey(1) # request maximum refresh rate

cv2.destroyAllWindows()

