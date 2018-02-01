#!/usr/bin/env python

from opencv.cv import *
from opencv.highgui import *

cvNamedWindow("w1", CV_WINDOW_AUTOSIZE)
capture = cvCreateCameraCapture(0)

def calculate( image ):
	greyscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
	cvCvtColor(image, greyscale, CV_BGR2GRAY)
	storage = cvCreateMemStorage(0)
	cvClearMemStorage(storage)
	cvEqualizeHist(greyscale, greyscale)
	cascade = cvLoadHaarClassifierCascade( '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml', cvSize(1,1))
	faces = cvHaarDetectObjects(greyscale, cascade, storage, 1.2, 2, CV_HAAR_DO_CANNY_PRUNING, cvSize(25,25))

	ret = []

	if faces:
		for f in faces:
			omghax = {}
			omghax['x1'] = f.x
			omghax['y1'] = f.y
			omghax['x2'] = f.x+f.width
			omghax['y2'] = f.y+f.height
			ret.append( omghax )
	return ret

def repeat():
	global capture

	width  = 320
	height = 240

	frame  = cvQueryFrame(capture)
	minime = cvCreateMat(height, width,cvGetElemType( frame ))
	cvResize(frame, minime)

	hax = calculate( minime )

	for l in hax:
		cvRectangle(
			minime,
			cvPoint( int(l['x1']), l['y1']),
			cvPoint(int(l['x2']), int(l['y2'])),
			CV_RGB(0, 255, 0),
			3, 8, 0)

	cvShowImage("w1", minime)
	c = cvWaitKey(2)

while True:
	repeat()
