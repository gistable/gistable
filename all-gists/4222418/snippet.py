import cv

CAMERA_INDEX = 0

# CODEC = cv.CV_FOURCC('D','I','V','3') # MPEG 4.3
# CODEC = cv.CV_FOURCC('M','P','4','2') # MPEG 4.2
# CODEC = cv.CV_FOURCC('M','J','P','G') # Motion Jpeg
# CODEC = cv.CV_FOURCC('U','2','6','3') # H263
# CODEC = cv.CV_FOURCC('I','2','6','3') # H263I
# CODEC = cv.CV_FOURCC('F','L','V','1') # FLV
CODEC = cv.CV_FOURCC('P','I','M','1') # MPEG-1
CODEC = cv.CV_FOURCC('D','I','V','X') # MPEG-4 = MPEG-1

# Initialize the camera for video capture
capture = cv.CaptureFromCAM(CAMERA_INDEX)

# Initialize the video writer to write the file
writer = cv.CreateVideoWriter(
    '/Users/sean/Desktop/out.avi',     # Filename
    CODEC,                              # Codec for compression
    25,                                 # Frames per second
    (640, 480),                         # Width / Height tuple
    True                                # Color flag
)

# Capture 50 frames and write each one to the file
for i in range(0, 25):
    print 'frame #:', i
    frame = cv.QueryFrame(capture)
    cv.ShowImage("w1", frame)
    cv.WriteFrame(writer, frame)

# Release the capture
del(capture)
del(writer)
print 'released capture'