"""
This demonstration assumes you have already installed Pymba and followed the installation instructions there:
https://github.com/morefigs/pymba

MoviePy is used to save the frames to a video file for later viewing, while the frame's mean intensity is
printed in real time. MoviePy can be installed from pip nicely.
"""
import pymba
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter as VidWriter
from skimage.color import gray2rgb
import time

# Start by getting the Vimba API set up
# Using the context (i.e. 'with' syntax) is a good idea
# If something crashes, vimba.shutdown() will get called automatically
# and your camera will not get left in an unusable state!
with pymba.Vimba() as vimba:
    print vimba.getVersion()
    
    # Find any cameras that are attached
    system = pymba.getSystem()
    system.runFeatureCommand("GeVDiscoveryAllOnce")
    time.sleep(0.2) # feature commands run in another thread, but need a moment to execute
    camera_ids = vimba.getCameraIds()
    
    # Just use the first camera we found
    vmb_cam = vimba.getCamera(camera_ids[0])
    vmb_cam.openCamera()
    
    # Set up the camera with the right parameters
    # Includes examples of setting up the output TTLs
    vmb_cam.PixelFormat = 'Mono8'
    vmb_cam.AcquisitionMode = 'Continuous'
    vmb_cam.BinningHorizontal = 4
    vmb_cam.BinningVertical = 4
    vmb_cam.Height = vmb_cam.HeightMax
    vmb_cam.Width = vmb_cam.WidthMax
    vmb_cam.AcquisitionFrameRateAbs = 60
    vmb_cam.SyncOutSelector = 'SyncOut1'
    vmb_cam.SyncOutSource = 'Exposing'
    vmb_cam.TriggerSource = 'FixedRate'
    
    # Set up the video file where our frames will be logged
    video_logger = VidWriter(filename="vimba_test.mp4",
                             size=(vmb_cam.Width, vmb_cam.Height),
                             fps=vmb_cam.AcquisitionFrameRateAbs,
                             code='mpeg4',
                             preset='ultrafast')
    
    # Now we set up a callback that will process frames as they arrive
    def frame_callback(frame):
        frame_data = frame.getBufferByteData()
        img = np.ndarray(buffer=frame_data,
                         dtype=np.uint8,
                         shape=(frame.height, frame.width))
        print img.mean()
        video_logger.write_frame(gray2rgb(img))
        frame.queueFrameCapture(frame_callback)
    
    # Finally, create a buffer of frames. Vimba's way of doing this
    # is odd: you just make a bunch of frame objects and Vimba decides
    # what order to fill them in.
    n_vimba_frames = 10
    frame_pool = [vmb_cam.getFrame() for _ in xrange(n_vimba_frames)]
    for frame in frame_pool:
        frame.announceFrame() # now Vimba knows about the frame... also odd design choice
        frame.queueFrameCapture(frame_callback)
        
    # Start capturing frames!
    vmb_cam.startCapture()
    vmb_cam.runFeatureCommand('AcquisitionStart')
    time.sleep(30) # 30 seconds of acquisition, proves that frames are written on another thread
    vmb_cam.runFeatureCommand('AcquisitionStop')
    time.sleep(0.2)
    vmb_cam.flushCaptureQueue() # unqueues all frames, must be called before endCapture()
    vmb_cam.endCapture()
    vmb_cam.revokeAllFrames() # makes Vimba forget about the frames it's just unqueued