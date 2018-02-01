#!/usr/local/bin/python
# coding: utf-8

import cv2
import sys
import numpy
from matplotlib import pyplot as plt
from scipy.spatial import distance

"""
OpenCV program to extract ticket stub images from photographs,
via automatic perspective correction for quadrilateral objects.
Intended for use prior to running through OCR.

Developed for the website http://stub.town by Mark Boszko

Based in large part on Python port of ScannerLite
    https://gist.github.com/scturtle/9052852
original C++
    https://github.com/daisygao/ScannerLite
Also incorporates ideas from:
    http://opencv-code.com/tutorials/automatic-perspective-correction-for-quadrilateral-objects/
    http://www.pyimagesearch.com/2015/04/06/zero-parameter-automatic-canny-edge-detection-with-python-and-opencv/
"""


class Line:
    """
    A line object
    """
    def __init__(self, l):
        self.point = l
        x1, y1, x2, y2 = l
        self.c_x = (x1 + x2) / 2
        self.c_y = (y1 + y2) / 2


def show(image):
    """
    Show any image.
    """
    msg = 'press any key to continue'
    cv2.namedWindow(msg, cv2.WINDOW_NORMAL)
    cv2.imshow(msg, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

def auto_canny(image, sigma=0.33):
    """
    Get edges of an image
    image: grayscale and blurred input image
    edged: canny edge output image
    """
    # compute the median of the single channel pixel intensities
    v = numpy.median(image)
    
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
 
    # return the edged image
    return edged


def intersection(l1, l2):
    """
    Compute intersect point of two lines l1 and l2
    l1: line
    l2: line
    return: Intersect Point
    """
    x1, y1, x2, y2 = l1.point
    x3, y3, x4, y4 = l2.point
    a1, b1 = y2 - y1, x1 - x2
    c1 = a1 * x1 + b1 * y1
    a2, b2 = y4 - y3, x3 - x4
    c2 = a2 * x3 + b2 * y3
    det = a1 * b2 - a2 * b1
    assert det, "lines are parallel"
    return (1. * (b2 * c1 - b1 * c2) / det, 1. * (a1 * c2 - a2 * c1) / det)


def scanCrop(image, debug=False):
    """
    Do the whole scanning thing.
    image: input image
    return: output image, cropped and perspective corrected
    """
    # resize input image to img_proc to reduce computation
    h, w = image.shape[:2]
    min_w = 300
    scale = min(10., w * 1. / min_w)
    h_proc = int(h * 1. / scale)
    w_proc = int(w * 1. / scale)
    image_dis = cv2.resize(image, (w_proc, h_proc))
    if debug:
        print(image.shape)
        print(image_dis.shape)

    # make grayscale
    gray = cv2.cvtColor(image_dis, cv2.COLOR_BGR2GRAY)

    # blur
    gray = cv2.GaussianBlur(gray, (5,5), 0)

    # get edges of the image
    canny = auto_canny(gray)
    if debug:
        show(canny)

    # extract lines from the edge image
    # TODO: Seem good for given scale, but need more test images to confirm
    threshold = 70
    minLineLength = w_proc / 10
    maxLineGap = w_proc / 30
    lines = cv2.HoughLinesP(canny, 1, numpy.pi/180, threshold, None, minLineLength, maxLineGap)


    if debug:
        t = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)

    # classify lines into horizontal or vertical
    hori, vert = [], []
    for l in lines[0]:
        x1, y1, x2, y2 = l
        if abs(x1 - x2) > abs(y1 - y2):
            hori.append(Line(l))
        else:
            vert.append(Line(l))
        if debug:
            cv2.line(t, (x1, y1), (x2, y2), (0, 0, 255), 1)
    if debug:
        show(t)

    # edge cases when not enough lines are detected
    # extend the known lines to the edge of the image to create a new line
    if len(hori) < 2:
        if not hori or hori[0].c_y > h_proc / 2:
            hori.append(Line((0, 0, w_proc - 1, 0)))
        if not hori or hori[0].c_y <= h_proc / 2:
            hori.append(Line((0, h_proc - 1, w_proc - 1, h_proc - 1)))

    if len(vert) < 2:
        if not vert or vert[0].c_x > w_proc / 2:
            vert.append(Line((0, 0, 0, h_proc - 1)))
        if not vert or vert[0].c_x <= w_proc / 2:
            vert.append(Line((w_proc - 1, 0, w_proc - 1, h_proc - 1)))

    # sort lines according to their center point
    hori.sort(key=lambda l: l.c_y)
    vert.sort(key=lambda l: l.c_x)

    # find corners
    
    if debug:
        # Visualize corners for debug only
        for l in [hori[0], vert[0], hori[-1], vert[-1]]:
            x1, y1, x2, y2 = l.point
            cv2.line(t, (x1, y1), (x2, y2), (0, 255, 255), 1)
    
    # corners for the small scale
    image_points = [intersection(hori[0], vert[0]), intersection(hori[0], vert[-1]),
               intersection(hori[-1], vert[0]), intersection(hori[-1], vert[-1])]
    if debug:
        print("image_points small", image_points)

    # scale corners to the original size
    for i, p in enumerate(image_points):
        x, y = p
        image_points[i] = (x * scale, y * scale)
        if debug:
            cv2.circle(t, (int(x), int(y)), 1, (255, 255, 0), 3)
    if debug:
        print("image_points large", image_points)
        show(t)

    # perspective transform
    
    # Proportional to the original image:
    # image_points[0] is Upper Left corner
    # image_points[1] is Upper Right corner
    # image_points[2] is Lower Left corner
    # image_points[3] is Lower Right corner
    
    top_width = distance.euclidean(image_points[0], image_points[1])
    bottom_width = distance.euclidean(image_points[2], image_points[3])
    # Average
    output_width = int((top_width + bottom_width) / 2)
    
    left_height = distance.euclidean(image_points[0], image_points[2])
    right_height = distance.euclidean(image_points[1], image_points[3])
    # Average
    output_height = int((left_height + right_height) / 2)
    
    if debug:
        print(top_width, bottom_width, output_width)
        print(left_height, right_height, output_height)
    
    dst_pts = numpy.array(
        ((0, 0), (output_width - 1, 0), (0, output_height - 1), (output_width - 1, output_height - 1)),
        numpy.float32)
    image_points = numpy.array(image_points, numpy.float32)
    transmtx = cv2.getPerspectiveTransform(image_points, dst_pts)
    return cv2.warpPerspective(image, transmtx, (output_width, output_height))


if __name__ == '__main__':
    """
    For testing
    test.jpg: expect image in same folder as script, with rectangular object
    test-crop.jpg: output cropped image; will overwrite if exists
    """
    image = cv2.imread('test.jpg')
    
    # If our test image needs to be rotated
    image = numpy.rot90(image, 3)
    
    show(image)
    output_image = scanCrop(image, debug=True)
    show(output_image)
    cv2.imwrite('test-crop.jpg',output_image)
    print("Saved.")