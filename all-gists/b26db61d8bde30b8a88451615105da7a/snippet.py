import base64 as b64
import numpy as np
import cv2
import matplotlib.pyplot as plt
from ipywidgets import interact, interactive, fixed
from IPython.display import Image, display
import ipywidgets as widgets
from itertools import tee, izip

WINDOW_SIZE = 41 # size of window to use when computing averages. Endpoint images outside 
                 # window range are not analyzed

def convert_media_to_image(media):
    arr = np.asarray(bytearray(b64.b64decode(media["__data__"])), dtype=np.uint8)
    return cv2.imdecode(arr,-1)

def window(iterable, size=3):
    iters = tee(iterable, size)
    for i in xrange(1, size):
        for each in iters[i:]:
            next(each, None)
    return izip(*iters)

def moving_averages(sequence, winsize=51):
    avgs = []
    segshape = list(sequence[0].shape)
    segshape.append(winsize)
    for segment in window(sequence, size=winsize):
        avg = np.zeros(segshape)
        for idx, im in enumerate(segment):
            avg[:,:,:,idx] = im
        avg = np.uint8(np.average(avg, axis=3))
        avgs.append(cv2.GaussianBlur(cv2.merge([avg[:,:,0], avg[:,:,1], 
                                                avg[:,:,2]]), (5,5), 2))
    return avgs

def display_image(image):
    _, png_image = cv2.imencode(".png", image)
    display(Image(data=png_image.tostring()))

def get_struct(size):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
    
def raw_edges(image, hmin=25, hmax=100):
    im = image.copy()
    edges = cv2.Canny(im, hmin, hmax)
    return edges

def dilate_edges(edges, image):  
    _edges = edges
    dst = image.copy()
    contours, _ = cv2.findContours(_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(dst, contours, -1, (255,255,255))
    return dst

def binary_mask(im, thresh=0, val=255):
    imgray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    th, binary = cv2.threshold(imgray, thresh, val, cv2.THRESH_BINARY)
    return binary

def open_and_close(binary, kopen, kclose, iteropen=1, iterclose=1):
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kopen, iteropen) 
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kclose, iterclose)
    return closing

def get_contours(im, min_area=0, max_area=None):
    _im = im.copy()
    contours, _ = cv2.findContours(_im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(c) for c in contours]
    if max_area is None:
        return [c for c, a in zip(contours, areas) if min_area <= a]
    return [c for c, a in zip(contours, areas) if min_area <= a <= max_area]
    
def fit_contours(contours):
    return [cv2.fitEllipse(c) for c in contours]

def detect_objects(src, diff, blursize=(3,3)):
    image = cv2.GaussianBlur(diff, blursize, 1)
    cimage = image.copy()
    cimage = cv2.medianBlur(cimage[:690, :700, :], 3) #crop ROI
    edges = raw_edges(cimage, hmin=50, hmax=150)
    dilated = dilate_edges(edges, cimage)
    binary = binary_mask(dilated, 65, 255)
    morphed = open_and_close(binary, get_struct(1), get_struct(5), iterclose=2)
#     morphed = cv2.morphologyEx(morphed, cv2.MORPH_DILATE, 5)
    contours = get_contours(morphed, min_area=300)
    return fit_contours(contours), dilated, morphed

# ------------------------------------------------------------------------
# NOTE: Unless changing window size and/or data range, it is wise to comment this 
# section out after an initial execution as these lines can be computationally expensive 
winsize = WINDOW_SIZE
images = [convert_media_to_image(rec['media']) for oid, rec in data[100:200]]
imdiffs = [cv2.absdiff(images[idx + (winsize-1)/2], avg) 
           for idx, avg in enumerate(moving_averages(images, winsize=winsize))]
# ------------------------------------------------------------------------

@interact(idx=widgets.IntSlider(min=0,max=len(imdiffs)-1,step=1,value=0))
def display_objects(idx):
    _idx = (winsize -1) /2 + idx
    ellipses, dilated, morphed = detect_objects(images[_idx], imdiffs[idx], blursize=(3,3))
    for e in ellipses:
        cv2.ellipse(images[_idx], e, (255,255,0), 1)
    print "Detected %i Cars" % len(ellipses)
    display_image(images[_idx])
#     display_image(dilated)
#     display_image(morphed)