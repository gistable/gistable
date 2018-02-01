# CamTracker.py - track a colourful object with a webcam mounted atop a servo
# Running on a Raspberry Pi, Raspbian Wheezy OS
# (c) Sakari Kapanen, 2013

import cv2
import numpy as np
from RPIO import PWM

# the HSV range we use to detect the colourful object
Hmin = 159
Hmax = 179 
Smin = 108
Smax = 255
Vmin = 80
Vmax = 255
# minimum detected area
minArea = 50
# frame parameters
width = 160
height = 120
cx = int(0.5 * width)
cy = int(0.5 * height)
# servo PWM pulsewidths
dServo = 20
servoVal = 1500
servoMin = 500
servoMax = 2500
# the maximum delta (pixels) when the object is still considered centered
eps = 15

rangeMin = np.array([Hmin, Smin, Vmin], np.uint8)
rangeMax = np.array([Hmax, Smax, Vmax], np.uint8)

cv2.namedWindow("Adjustment")
cv2.namedWindow("Video")
cv2.namedWindow("Binary")

def nothing(*args):
  pass

def updateRanges():
  Hmin = cv2.getTrackbarPos("Hmin", "Adjustment")
  Hmax = cv2.getTrackbarPos("Hmax", "Adjustment")
  Smin = cv2.getTrackbarPos("Smin", "Adjustment")
  Smax = cv2.getTrackbarPos("Smax", "Adjustment")
  Vmin = cv2.getTrackbarPos("Vmin", "Adjustment")
  Vmax = cv2.getTrackbarPos("Vmax", "Adjustment")
  minArea = cv2.getTrackbarPos("minArea", "Adjustment")
  rangeMin = np.array([Hmin, Smin, Vmin], np.uint8)
  rangeMax = np.array([Hmax, Smax, Vmax], np.uint8)
  return rangeMin, rangeMax, minArea

# create controls for adjusting the detection range
cv2.createTrackbar("Hmin", "Adjustment", Hmin, 179, nothing)
cv2.createTrackbar("Hmax", "Adjustment", Hmax, 179, nothing)
cv2.createTrackbar("Smin", "Adjustment", Smin, 255, nothing)
cv2.createTrackbar("Smax", "Adjustment", Smax, 255, nothing)
cv2.createTrackbar("Vmin", "Adjustment", Vmin, 255, nothing)
cv2.createTrackbar("Vmax", "Adjustment", Vmax, 255, nothing)
cv2.createTrackbar("minArea", "Adjustment", minArea, 1000, nothing)
# capture from the first webcam found
cap = cv2.VideoCapture(0)

if cap.isOpened():
  cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)
  cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)

  servo = PWM.Servo()
  servo.set_servo(4, servoVal)
  while True:
    servo.set_servo(4, servoVal)
    # read a frame
    ret, image = cap.read()
    # blur the frame
    image = cv2.blur(image, (3, 3))
    # convert to HSV
    imgHSV = cv2.cvtColor(image, cv2.cv.CV_BGR2HSV)
    rangeMin, rangeMax, minArea = updateRanges()
    # pixels within range are set to 1, others to 0
    imgThresh = cv2.inRange(imgHSV, rangeMin, rangeMax)
    #imgThresh = cv2.blur(imgThresh, (2, 2))

    # calculate image moments
    moments = cv2.moments(imgThresh, True)
    if moments['m00'] >= minArea:
      # calculate the centroid of the object using the moments
      x = moments['m10'] / moments['m00']
      y = moments['m01'] / moments['m00']
      cv2.circle(image, (int(x), int(y)), 5, (0, 255, 0), -1)
      # move the servo if necessary, check limits
      dx = x - cx
      step = abs(int(dx / 20) * dServo)
      if (x - cx) > eps:
        servoVal += step
      elif (cx - x) > eps:
        servoVal -= step
      if servoVal < servoMin:
        servoVal = servoMin
      if servoVal > servoMax:
        servoVal = servoMax

    cv2.imshow("Video", image)
    cv2.imshow("Binary", imgThresh)
    key = cv2.waitKey(10) 
    if key == 27:
      break

cv2.destroyAllWindows()
