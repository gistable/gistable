#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script was originally created by by killagreg î Thu Dec 18, 2014  7:53 am
# see   http://www.raspberrypi.org/forums/viewtopic.php?p=656881#p656881

# This script implements a motion capture surveillance cam for raspberry pi using picam
# and is based on the picamera python library.
# It uses the "motion vectors" magnitude of the h264 hw-encoder to detect motion activity.

# Modified by spikedrba 2015-02-02 (mostly code cleanup, removing snapshotting and trying to add mjpeg streaming)

import os
import logging
import logging.handlers
import threading
import subprocess
import io
import picamera
import picamera.array
import numpy as np
import datetime as dt
import time
from PIL import Image

pmd_version = "v1-spike" #current version number to print in the logger

#logging_level = logging.INFO
logging_level  = logging.DEBUG

# extra debugging - dump histo on all frames where some threshold motion is detected (CPU INTENSIVE !)
debug_dump_extra_motion_histo = False

#dump_png mode? dumps extra dump_png info.  Note: it doesn't work.
dump_png = False

# define a timeout for the "event" waiting for motion to be detected,
# so that other processing can occur when a timeout occurs, eg jpeg snapshots
motion_event_wait_timeout = 300 # seconds

filepath = '/var/www/pmd'
logger_filename = filepath + '/pmd.log'

# setup pre and post video recording around motion events
video_preseconds = 2   # minimum 1
video_postseconds = 2  # minimum 1

# setup the main video/snapshot camera resolution
# see this link for a full discussion on how to choose a valid resolution that will work
# http://picamera.readthedocs.org/en/latest/fov.html
video_width = 1296
video_height = 730

video_framerate = 45 # setup the camera video framerate

# setup the camera h264 GOP size (I frames and their subsequent P and B friends)
# the *higher* this value
#  - the more actual video we "lose" whilst delayed waiting for "splitting" to finish (it seeks the next I frame)
#  - the smaller the h264 filesize since it will use more (and smaller) B and P intra-I frames
video_intra_period = 5

#setup video rotation (0, 90, 180, 270)
video_rotation = 180

# setup the camera to perform video stabilization
#video_stabilization = True
video_stabilization = False

# setup the camera to put a black background on the annotation (in our case, for date/time)
#video_annotate_background = True
video_annotate_background = False

# setup the camera to put frame number in the annotation
#video_annotate_frame_num = True
video_annotate_frame_num = False

# we could setup a webcam mode, to capture images on a regular interval in between motion recordings
# setup jpeg capture snapshot flag and filename prefix
perform_snapshot_capture = False
snapshot_capture_filename = "snapshot"

# define motion detection video resolution, equal or smaller than capture video resolution
# *smaller* = less cpu needed thus "better" and less likely to lose frames etc
motion_width  = 640
motion_height = 480

# setup motion detection threshold,
# i.e. magnitude of a motion block to count as  motion
motion_threshold = 6

# setup motion detection sensitivity,
# i.e number of motion blocks that trigger a motion detection
# eg 640x480 resolution results in 41 x 30 motion blocks, 5% of 1230=61
# eg 640x360 resolution results in 41 x 23 motion blocks, 5% of 1230=61
# eg 320x240 resolution results in 21 x 15 motion blocks, 5% of 315=15
motion_sensitivity = 4

# define a shell cmd that should be executed when motion has been recognized
motion_cmd = ""
#motion_cmd = filepath + '/pmd_motion_detected.sh'

# define an event used to set/clear/check whether motion was detected or not-detected
# with any luck, this means that we won't use 100% cpu looping around
# inside a WHILE TRUE loop just constantly checking for a true/false condition
motion_event = threading.Event()
motion_event.clear()

# initialize timestamp stuff
motion_timestamp = time.time()
motion_window_active = "-"
motion_frame_active = "-"

prev_frame_annotation = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " --"
curr_frame_annotation = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " --"

# calculate trhe number of blocks that motion vectors have
# and initialize a regions of of interest array with zeroes
motion_cols = (motion_width  + 15) // 16 + 1
motion_rows = (motion_height + 15) // 16
if dump_png:
    motion_array = np.zeros((motion_rows, motion_cols), dtype = np.uint8)

# pre-initialise arrays for histograms (print these in the log)
histo_bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50, 100]
histo0 =     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 00, 00, 00, 00, 00, 00, 000]
histo1 =     histo0
histo2 =     histo0
histo_nil =  histo0
histo_extra_debug = histo0

#call back handler for motion output data from h264 hw encoder
#this processes the motion vectors from the low resolution splitted capture
class MyMotionDetector(picamera.array.PiMotionAnalysis):
   th_counter = 0       # static variable within the class

   def analyse(self, a):
      global histo1, histo2, debug_dump_extra_motion_histo, histo_extra_debug
      global camera, motion_event, motion_timestamp, motion_array, motion_array_mask
      global prev_frame_annotation, curr_frame_annotation, motion_window_active, motion_frame_active
      # calculate length of motion vectors of mpeg macro blocks
      a = np.sqrt(
          np.square(a['x'].astype(np.float)) +
          np.square(a['y'].astype(np.float))
          ).clip(0, 255).astype(np.uint8)
      # If there's more than 'sensitivity' number vectors with a magnitude greater than 'threshold', then say we've detected motion
      th = ((a > motion_threshold).sum() > motion_sensitivity)
      now = time.time()
# by now ...
# th                     = motion detected on current frame
# motion_timestamp       = the last time when motion was detected in a frame (start of time window)
# motion_event.is_set()  = whether motion detection time window is currently triggered
#                        = is only turned off if motion has previously been detected
#                          and both "no motion detected" and its time window has expired
      if th:
          motion_timestamp = now
          motion_frame_active = "f"
          #logger.debug('frame motion detected')
          if debug_dump_extra_motion_histo:
              histo_extra_debug, histo_nil = np.histogram(a, bins=histo_bins, density=False) # hopefully this resets the "bin counts" too
              logger.debug("Histo motion frame: " + str(histo_extra_debug))
      else:
          motion_frame_active = "-"

      # MOTION DETECTION PROCESSING
      # if motion is detected, don't clear the detection flag until video_postseconds have passed
      if motion_event.is_set():
          if (now - motion_timestamp) >= video_postseconds:
              motion_event.clear()
              MyMotionDetector.th_counter = 0
              motion_window_active = "-"
              logger.debug('Capture time window cleared')
      else:
          if th:
              MyMotionDetector.th_counter += 1
              if (MyMotionDetector.th_counter == 1): # only 1      consecutive motion thresholds
                  # create a histogram to describe the frame motion thresholds that were detected upon first detection
                  histo1, histo_nil = np.histogram(a, bins=histo_bins, density=False) # hopefully this resets the "bin counts" too
              elif (MyMotionDetector.th_counter == 2): # matched 2   consecutive motion thresholds
                  # create a histogram to describe the frame motion thresholds that were detected upon second detection
                  histo2, histo_nil = np.histogram(a, bins=histo_bins, density=False) # hopefully this resets the "bin counts" too
                  motion_event.set()
                  motion_window_active = "w"
                  logger.debug('Second consecutive frame motion detected - capture time window set.')
                  if dump_png: # the dump_png .png file doesn't work
                      idx = a > motion_threshold
                      a[idx] = 255
                      motion_array = a
              elif (MyMotionDetector.th_counter > 2): # more than 2 consecutive motion thresholds
                  histo1 = histo0
                  histo2 = histo0
          else:
              # decrement threshold counter when a non-motion detection frame occurs
              #if(MyMotionDetector.th_counter):
                  #MyMotionDetector.th_counter -= 1
              if(MyMotionDetector.th_counter > 0):
                  MyMotionDetector.th_counter = 0

      # annotate the frame
      curr_frame_annotation = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + motion_window_active + motion_frame_active
      if  curr_frame_annotation != prev_frame_annotation:
          camera.annotate_text = curr_frame_annotation
          prev_frame_annotation = curr_frame_annotation

# Write the entire content of the circular buffer to disk. No need to
# lock the stream here as we're definitely not writing to it
# simultaneously
def write_video(stream):
     global motion_filename

     with io.open(motion_filename + '-before.h264', 'wb') as output:
         for frame in stream.frames:
             if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                 stream.seek(frame.position)
                 break
         while True:
             buf = stream.read1()
             if not buf:
                 break
             output.write(buf)
     # Wipe the circular stream once we're done
     stream.seek(0)
     stream.truncate()

# use asynchronous threads to perform some command processing in the background
# and therefore  does not hold up processing waiting for that command to complete
class execute_cmd_asynchronously (threading.Thread):
    def __init__(self, threadID, cmd):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.cmd = cmd
    def run(self):
        subprocess.call(self.cmd, shell=True)

def run_background(threadID, cmd):
    if(cmd != ""):
      thread = execute_cmd_asynchronously(threadID, cmd)
      thread.start()

## MAIN

logger = logging.getLogger('pmd')
logger.setLevel(logging_level)
fh = logging.handlers.RotatingFileHandler(logger_filename, mode='a', maxBytes=(1024*1000 * 2), backupCount=5, delay=0)
fh.setLevel(logging_level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.info('----------------------------------------')
logger.info('pmd %s has been started' % (pmd_version))
logger.info('----------------------------------------')
logger.info("Video capture filepath: %s" % (filepath))
logger.info("Capture videos with %d x %d resolution" % (video_width, video_height))
logger.info("Analyse motion vectors from a %d x %d resolution split" % (motion_width, motion_height))
logger.info("  resulting in %d x %d motion blocks" % (motion_cols, motion_rows))
logger.info("Analyse motion vectors threshold , sensitivity: %d , %d" % (motion_threshold, motion_sensitivity))
logger.info("Framerate: %d fps" % (video_framerate))
logger.info("video_intra_period: %d" % (video_intra_period))
logger.info("Rotation: %d degrees" % (video_rotation))
logger.info("Stabilization: %r" % (video_stabilization))
logger.info("Annotate background: %r" % (video_annotate_background))
logger.info("Annotate frame_num: %r" % (video_annotate_frame_num))
logger.info("Video detection event capture before-seconds , after-seconds: %d , %d" % (video_preseconds, video_postseconds))
logger.info("motion_event_wait_timeout: %s" % (motion_event_wait_timeout))
logger.info("perform_snapshot_capture: %r" % (perform_snapshot_capture))
logger.info("snapshot_capture_filename: %s" % (snapshot_capture_filename))
logger.info("logger_filename: %s" % (logger_filename))
logger.info("Histo_frame motion threshold bins: " + str(histo_bins))
logger.info("Logging Level: %d (info=%d, debug=%d)" % (logging_level, logging.INFO, logging.DEBUG))
logger.info("Dump extra motion histo info: %r" % (debug_dump_extra_motion_histo))

with picamera.PiCamera() as camera:
   camera.resolution = (video_width, video_height)
   camera.framerate = video_framerate
   camera.rotation = video_rotation
   camera.video_stabilization = video_stabilization
   camera.annotate_background = video_annotate_background
   camera.annotate_frame_num = video_annotate_frame_num

   # setup a circular IO buffer to contain video of "before motion detection" footage
   stream = picamera.PiCameraCircularIO(camera, seconds = video_preseconds)

   # 1. split the hi resolution video recording into circular buffer from splitter port 1
   # note: splitting video recording happens at a key frame, so see parameter video_intra_period
   camera.start_recording(stream, format='h264', splitter_port=1, inline_headers=True, intra_period=video_intra_period)

   # 2. split the low resolution motion vector analysis from splitter port 2, throw away the actual video
   camera.start_recording('/dev/null', splitter_port=2, resize=(motion_width,motion_height) ,format='h264', motion_output=MyMotionDetector(camera, size=(motion_width,motion_height)))

   # wait some seconds for stable video data to be available
   camera.wait_recording(2, splitter_port=1)
   joiner_thread_id = 0
   logger.info('OK. Commence waiting for first REAL motion to be detected')
   try:
       while True: #might be causing high CPU usage?
          logger.info("Entering event wait state awaiting next motion detection by class MyMotionDetector ...")
          motion_event.clear()
          logger.debug("(also, window capture status was reset prior to waiting for motion event)")

          if motion_event.wait(motion_event_wait_timeout):
             histo1_tmp = histo1
             histo2_tmp = histo2
             logger.info('Detected motion')
             logger.info("Histo frame 1: " + str(histo1_tmp))
             logger.info("Histo frame 2: " + str(histo2_tmp))
             motion_filename = filepath + "/" + time.strftime("%Y%m%d-%H%M%S", time.localtime(motion_timestamp))
             # split  the high res video stream to a file instead of to the internal circular buffer
             logger.debug('splitting video from circular IO buffer to after-motion-detected h264 file ')
             camera.split_recording(motion_filename + '-after.h264', splitter_port=1)

             # save circular buffer containing "before motion" event video, ie write it to a file
             logger.debug('started  saving before-motion circular buffer')
             write_video(stream)
             logger.debug('finished saving before-motion circular IO buffer')
             #---- wait for the end of motion event here, in one second increments
             logger.debug('start waiting to detect end of motion')
             #while motion_detected stay inside the loop below, recording
             while motion_event.is_set():
                camera.wait_recording(0.5, splitter_port=1)
             #---- end of motion event detected
             logger.info('Detected end of motion')
             #split video recording back in to circular buffer at next key frame (see parameter video_intra_period)
             logger.debug('splitting video back into the circular IO buffer')
             camera.split_recording(stream, splitter_port=1)

             # transcode to h264, using a separate thread to avoid blocking this loop
             joiner_cmd = "cat %s %s > %s && rm -f %s && rm -f %s" % (motion_filename + "-before.h264", motion_filename + "-after.h264", motion_filename + ".h264", motion_filename + "-before.h264", motion_filename + "-after.h264")
             joiner_thread_id = joiner_thread_id + 1
             logger.debug("starting new video post-processing thread %d for h264 files" % (joiner_thread_id))
             logger.debug(joiner_cmd)
             run_background(joiner_thread_id, joiner_cmd)
             logger.info("Finished motion capture processing after detecting end-of-motion.")
          else:
             # no motion detected or in progress
             logger.debug("Motion detector timed out")
             # if webcam mode, capture images on the regular timeout interval
             if perform_snapshot_capture:
                 #snapf = filepath + "/" + snapshot_capture_filename + "-" + time.strftime("%Y%m%d-%H%M%S", time.gmtime(motion_timestamp))
                 snapf = filepath + "/" + snapshot_capture_filename + "-" + time.strftime("%Y%m%d-%H%M%S", time.localtime(time.time()))
                 camera.capture_sequence([snapf + ".jpg"], use_video_port=True, splitter_port=0)
                 logger.info("Captured snapshot")

   finally:
       camera.stop_recording(splitter_port=1)
       camera.stop_recording(splitter_port=2)
