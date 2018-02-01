# USAGE
# python face_detection.py --image face1.jpg

# import the necessary packages
# from imutils import face_utils
# import numpy as np
import argparse
import imutils
import dlib
import cv2
# from matplotlib import pyplot as plt

def rect_to_bb(rect):
    # take a bounding predicted by dlib and convert it
    # to the format (x, y, w, h) as we would normally do
    # with OpenCV
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y

    # return a tuple of (x, y, w, h)
    return (x, y, w, h)


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to input image")
args = vars(ap.parse_args())

# load the input image, resize it, and convert it to grayscale
image = cv2.imread(args["image"])
image = imutils.resize(image, width=500)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
detector = dlib.get_frontal_face_detector()

# detect faces in the grayscale image
rects = detector(gray, 1)
print(len(rects))

fname = args["image"].split('/')[-1]
name, ext = fname.split('.')

# loop over the face detections
for (i, rect) in enumerate(rects):
    # determine the facial landmarks for the face region, then
    # convert the landmark (x, y)-coordinates to a NumPy array
    (x, y, w, h) = rect_to_bb(rect)
    print(i, x, y, w, h)

    fname = '{}_{}.{}'.format(name, i, ext)
    # clone the original image so we can draw on it, then
    # display the name of the face part on the image
    clone = image.copy()
    cv2.rectangle(clone, (x, y), (x + w, y + h), (0, 255, 0), 1)
    startX = x
    startY = y - 15 if y - 15 > 15 else y + 15
    cv2.putText(clone, str(i), (startX, startY),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    roi = image[y:y + h, x:x + w]
    cv2.imshow("ROI", roi)
    cv2.imwrite(fname, roi)
    cv2.imshow("Image", clone)
    cv2.waitKey(0)
