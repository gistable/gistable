from __future__ import division
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

os.chdir('C:/Users/gennady.nikitin/Dropbox/Coding/OpenCV')

# define variable for resize tratio
ratio = 1

def for_point_warp(cnt, orig):
    # we need to determine
    # the top-left, top-right, bottom-right, and bottom-left
    # points so that we can later warp the image -- we'll start
    # by reshaping our contour to be our finals and initializing
    # our output rectangle in top-left, top-right, bottom-right,
    # and bottom-left order
    pts = cnt.reshape(4, 2)
    rect = np.zeros((4, 2), dtype = "float32")

    # summing the (x, y) coordinates together by specifying axis=1
    # the top-left point has the smallest sum whereas the
    # bottom-right has the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # compute the difference between the points -- the top-right
    # will have the minumum difference and the bottom-left will
    # have the maximum difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # Notice how our points are now stored in an imposed order: 
    # top-left, top-right, bottom-right, and bottom-left. 
    # Keeping a consistent order is important when we apply our perspective transformation

    # now that we have our rectangle of points, let's compute
    # the width of our new image
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))

    # ...and now for the height of our new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))

    # take the maximum of the width and height values to reach
    # our final dimensions
    maxWidth = max(int(widthA), int(widthB))
    maxHeight = max(int(heightA), int(heightB))

    # construct our destination points which will be used to
    # map the screen to a top-down, "birds eye" view
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")

    # calculate the perspective transform matrix and warp
    # the perspective to grab the screen
    M = cv2.getPerspectiveTransform(rect, dst)
    warp = cv2.warpPerspective(orig, M, (maxWidth, maxHeight))
    return warp

def resize(img, width=None, height=None, interpolation = cv2.INTER_AREA):
    global ratio
    w, h, _ = img.shape

    if width is None and height is None:
        return img
    elif width is None:
        ratio = height/h
        width = int(w*ratio)
        print(width)
        resized = cv2.resize(img, (height, width), interpolation)
        return resized
    else:
        ratio = width/w
        height = int(h*ratio)
        print(height)
        resized = cv2.resize(img, (height, width), interpolation)
        return resized

#load an image
flat_object = cv2.imread('1000.jpg')
#resize the image
flat_object_resized = resize(flat_object, height=600)
#make a copy
flat_object_resized_copy = flat_object_resized.copy()
#convert to HSV color scheme
flat_object_resized_hsv = cv2.cvtColor(flat_object_resized_copy, cv2.COLOR_BGR2HSV)
# split HSV to three chanels
hue, saturation, value = cv2.split(flat_object_resized_hsv)
# threshold to find the contour
retval, thresholded = cv2.threshold(saturation, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
# morphological operations
thresholded_open = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, (7,7))
thresholded_close = cv2.morphologyEx(thresholded_open, cv2.MORPH_CLOSE, (7,7))
# find edges
thresholded_edge = cv2.Canny(thresholded_close, 15, 150)
# The cv2.findContours method is destructive (meaning it manipulates the image you pass in) 
# so if you plan on using that image again later, be sure to clone it. 
cnts = cv2.findContours(thresholded_edge.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
# keep only 10 the largest ones
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
# the contour that we seek for
our_cnt = None
# loop over our 10 largest contours in the query image
for c in cnts:
    # approximate the contour
    # These methods are used to approximate the polygonal curves of a contour. 
    # In order to approximate a contour, you need to supply your level of approximation precision. 
    # In this case, we use 2% of the perimeter of the contour. The precision is an important value to consider. 
    # If you intend on applying this code to your own projects, you’ll likely have to play around with the precision value.
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    # if our approximated contour has four points, then
    # we can assume that we have found our screen
    if len(approx) == 4:
        our_cnt = approx
        break

# draw a contour
cv2.drawContours(flat_object_resized_copy, [our_cnt], -1, (0,255,0), 3)
warped = for_point_warp(our_cnt/ratio, flat_object)
warped = resize(warped, height=800)

cv2.imshow("Original image", flat_object_resized)
cv2.imshow("Marked ROI", flat_object_resized_copy)
cv2.imshow("Warped ROI", warped)

cv2.waitKey()
cv2.destroyAllWindows()