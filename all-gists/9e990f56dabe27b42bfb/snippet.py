#!/usr/bin/env python

import io
import time
import picamera
import picamera.array
import numpy as np
from PIL import Image, ImageDraw


FILE_PATTERN = 'motion%02d.h264' # the file pattern in which to record videos
FILE_BUFFER = 1048576            # the size of the file buffer (bytes)

REC_RESOLUTION = (1280, 720) # the recording resolution
REC_FRAMERATE = 24           # the recording framerate
REC_SECONDS = 10             # number of seconds to store in ring buffer
REC_BITRATE = 1000000        # bitrate for H.264 encoder

MOTION_MAGNITUDE = 60        # the magnitude of vectors required for motion
MOTION_VECTORS = 10          # the number of vectors required to detect motion


class MotionDetector(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, size=None):
        super(MotionDetector, self).__init__(camera, size)
        self.vector_count = 0
        self.detected = 0

    def analyse(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater than 60,
        # then set the last detected timestamp to now. Note: this is a really
        # crude method - I'm sure someone can do better with a bit of effort!
        # Things to try: filtering on SAD numbers, checking consecutive frames
        # for consistent motion in the same vectors, checking adjacent macro
        # blocks for similar motion vectors (to determine shape/size of moving
        # object). Then there's exposure, AWB, night/day cycles and such like
        # to compensate for
        vector_count = (a > MOTION_MAGNITUDE).sum()
        if vector_count > MOTION_VECTORS:
            self.detected = time.time()
            # We only store the count of vectors here as a demo of how to
            # easily extract some stats from the motion detector for debugging
            self.vector_count = vector_count


def create_recording_overlay(camera):
    # Make a recording symbol (red circle) overlay. This isn't perfect as
    # overlays don't support alpha transparency (so there'll be black corners
    # around the red circle) but oh well, it's only a demo!
    img = Image.new('RGB', (64, 64))
    d = ImageDraw.Draw(img)
    d.ellipse([(0, 0), (63, 63)], fill='red')
    o = camera.add_overlay(img.tostring(), size=img.size)
    o.alpha = 128
    o.layer = 1
    o.fullscreen = False
    o.window = (32, 32, 96, 96)
    return o


def main():
    with picamera.PiCamera() as camera:
        camera.resolution = REC_RESOLUTION
        camera.framerate = REC_FRAMERATE
        # Let the camera settle for a bit. This avoids detecting motion when
        # it's just the white balance and exposure settling.
        time.sleep(2)

        # Set up all the stuff we need: an overlay to indicate when we're
        # recording, the ring-buffer we want to record to when we haven't
        # detected motion, the file-object we want to record video to when
        # we *have* detected motion, and finally the motion detector itself
        camera.start_preview()
        recording_overlay = create_recording_overlay(camera)
        ring_buffer = picamera.PiCameraCircularIO(
            camera, seconds=REC_SECONDS, bitrate=REC_BITRATE)
        file_number = 1
        file_output = io.open(
            FILE_PATTERN % file_number, 'wb', buffering=FILE_BUFFER)
        motion_detector = MotionDetector(camera)

        # Start recording data to the ring buffer and the motion detector
        # at the specified bitrates
        camera.start_recording(
            ring_buffer, format='h264', bitrate=REC_BITRATE,
            intra_period=REC_FRAMERATE, motion_output=motion_detector)
        try:
            while True:
                # Motion not detected state:
                # In this state we just wait around for the motion detector to
                # notice something. We check whether the last motion detected
                # timestamp occurred in the last second
                print('Waiting for motion')
                while motion_detector.detected < time.time() - 1:
                    camera.wait_recording(1)

                # Transition to motion detected state:
                # Show the recording indicator, copy the content of the ring
                # buffer to the output file, then split the recording to the
                # output file. Note: because this is a file *we* opened
                # (instead of picamera opening it for us when we specify a
                # filename), we get to control when it closes, and picamera
                # doesn't move the file-pointer except when writing to it
                print('Motion detected (%d vectors)' % motion_detector.vector_count)
                print('Recording to %s' % file_output.name)
                recording_overlay.layer = 3
                with ring_buffer.lock:
                    for frame in ring_buffer.frames:
                        if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                            ring_buffer.seek(frame.position)
                            break
                    while True:
                        buf = ring_buffer.read1()
                        if not buf:
                            break
                        file_output.write(buf)
                camera.split_recording(file_output)
                # Clear the ring buffer (the easiest way to do this is simply
                # to reconstruct it). Note to self: add a clear() method to
                # the next version...
                ring_buffer = picamera.PiCameraCircularIO(
                    camera, seconds=REC_SECONDS, bitrate=REC_BITRATE)

                # Motion detected state:
                # Wait for REC_SECONDS without motion
                while motion_detector.detected > time.time() - REC_SECONDS:
                    camera.wait_recording(1)

                # Transition back to motion not detected state:
                # Split the recording back to the ring buffer, hide the
                # recording indicator, and open the next output file
                recording_overlay.layer = 1
                camera.split_recording(ring_buffer)
                file_number += 1
                file_output.close()
                file_output = io.open(
                    FILE_PATTERN % file_number, 'wb', buffering=FILE_BUFFER)
        finally:
            camera.stop_recording()

if __name__ == '__main__':
    main()
