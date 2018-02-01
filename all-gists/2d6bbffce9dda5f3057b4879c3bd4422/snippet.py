#! /usr/bin/env python
'''
greenscreen.py:  Greenscreen effect without a physical green screen
This performs background subtraction, and sets the background to "green" for use with "key frame" video editing software
Author: Scott Hawley, https://github.com/drscotthawley


Requirements:
Python, NumPy and OpenCV
I got these via Macports, but Homebrew, etc. work.  
Note that on Mac OS X El Capitan, OpenCV > 3.0 causes code to crash after ~30 seconds.  I had to install OpenCV 3.0 by hand.


Credits:
Built from Tutorial "Getting Started with Videos"
http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_video_display/py_video_display.html

Background-subtraction tutorials were of minimal utility and effectiveness, IMHO.  Developed
   my own foreground masking method for this

De-noising: http://docs.opencv.org/master/d5/d69/tutorial_py_non_local_means.html#gsc.tab=0

Cropping: http://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/

Time-averaging tutorial (not actually a great effect for this, but I left it in the code): 
       https://opencvpython.blogspot.com/2012/07/background-extraction-using-running.html
'''

import numpy as np
import cv2
import sys

source = 0   					# defaults to local (laptop) camera

if len(sys.argv) > 1:
	if ('-h' == sys.argv[1]) or ('--help'==sys.argv[1]):
		print "usage: greenscreen.py [-h,--help] [input_file]"
		print "   If input_file is blank, defaults to live camera capture"
		sys.exit()
	source = sys.argv[1]

cap = cv2.VideoCapture(source)    # Start the video source

ret, ref_img = cap.read()         # read background image

if (False == ret):
	print "Unable to get any images.  Is the camera already in use?"
	sys.exit()


# setup for reading & writing movie files
if (source !=0):                   
	fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
	video_out = cv2.VideoWriter()
	frame_shape = (ref_img.shape[1],ref_img.shape[0])
	success = video_out.open('greenscreen_movie_post.mp4v',fourcc, 15.0, frame_shape,True)


# initializing background arrays
green_img = np.zeros(ref_img.shape, np.uint8)
fgmask = np.zeros(ref_img.shape, np.uint8)
green_img[:] = (0, 255, 0)
orig_ref = ref_img
orig_green = green_img
result = ref_img 


# this is for automatically setting corners of frame to background
gray_shape = (ref_img.shape[0],ref_img.shape[1])
bg_edges = np.zeros(gray_shape, np.uint8)
# storage format is y,x, color
edge_size_x = bg_edges.shape[1]/8
edge_size_y = bg_edges.shape[0]/4
bg_edges[0:edge_size_y,0:edge_size_x] = 255
bg_edges[0:edge_size_y,-edge_size_x:] = 255
bg_edges[-edge_size_y:,0:edge_size_x] = 255
bg_edges[-edge_size_y:,-edge_size_x:] = 255


avg1 = np.float32(ref_img)   # time-averaging array



'''
find_fgmask: Finds the 'foregound mask', i.e. where the foreground objects are
Author: Scott Hawley
It doesn't use any especially clever algorithm (e.g., no BGMOG), just the fruits
of significant trial-and-error on my part, for what seems to work best

Warning: de-noising is slow, and best suited for post-processing only
'''
def find_fgmask(img,ref_img,thresh=13.0,use_denoise=False,h=10.0):
	diff1 = cv2.subtract(img,ref_img)
	diff2 = cv2.subtract(ref_img,img)
	diff = diff1+diff2 
	
	sws = int(   np.ceil(21*h/10) // 2 * 2 + 1 )
	diff[ abs(diff) < thresh] = 0
	gray = cv2.cvtColor(diff.astype(np.uint8), cv2.COLOR_BGR2GRAY)
	gray[np.abs(gray) < 10] = 0
	if (use_denoise):		
		cv2.fastNlMeansDenoising(gray,gray,h=h,templateWindowSize=5,searchWindowSize=sws)
	fgmask = gray.astype(np.uint8)
	fgmask[ fgmask >0] = 255
	return fgmask 



# Cropping stuff
refPt = []
setting_cropping = False
def click_and_crop(event, x, y, flags, param):
	# grab references to the global variables
	global refPt, cropping

	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping specification is being
	# performed
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		setting_cropping = True

	# check to see if the left mouse button was released
	elif event == cv2.EVENT_LBUTTONUP:
		# record the ending (x, y) coordinates and indicate that
		# the cropping operation is finished
		refPt.append((x, y))
		setting_cropping = False

		# draw a rectangle around the region of interest
		cv2.rectangle(result, refPt[0], refPt[1], (255, 255, 0), 2)
		cv2.imshow("frame", result)


cv2.namedWindow("frame")
cv2.setMouseCallback("frame", click_and_crop)  # register mouse events


print "Controls:"
print "D = difference image: take reference image & subtract"
print "C = clear settings: clear reference image, denoising"
print "T = toggle time averaging (probably don't want to use this)"
print "K = toggle crop (Draw box with mouse first, then press K)"
print "N = toggle de-noising (slow)"
print "Up/Down arrows = threshold for foreground: more/less green"
print "Left/Right arrows = size of denoising kernel: less/more noise"
print "Q = quit"

# control parameters
use_diff = True 
use_time_avg = False
use_denoise = False
denoise_h = 10.0
use_cropping = False
thresh = 13.0
already_pressed_clear = False
use_edges = False



# Main Loop
while(1):
	ret, img = cap.read()
	if (False==ret):   # end of video capture
		print "Saving and terminating"
		break

	# crop first, for speed
	if (use_cropping) and (len(refPt)==2):
		cropped_img = img[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]	
		img = cropped_img	
		if (img.shape[0] < ref_img.shape[0]) and (img.shape[1] < ref_img.shape[1]):
			cropped = ref_img[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
			ref_img = cropped
		if (img.shape[0] < green_img.shape[0]) and (img.shape[1] < green_img.shape[1]):
			cropped = green_img[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
			green_img = cropped
		if (img.shape[0] < avg1.shape[0]) and (img.shape[1] < avg1.shape[1]):
			avg1 = np.float32(ref_img)

	result = img 

	if (use_time_avg):
		cv2.accumulateWeighted(img,avg1,0.09)
		img = cv2.convertScaleAbs(avg1)

	if (use_diff):
		fgmask = find_fgmask(img,ref_img,thresh=thresh,use_denoise=use_denoise,h=denoise_h)
		bgmask = cv2.bitwise_not(fgmask)

		if (use_edges):
			bgmask = cv2.bitwise_or(bgmask,bg_edges)
			fgmask = cv2.bitwise_not(bgmask)

		fgimg = cv2.bitwise_and(img,img,mask = fgmask)
		bgimg = cv2.bitwise_and(green_img,green_img,mask = bgmask)

		sum = cv2.add(fgimg, bgimg)
		result = sum

	# if there's a cropping rectangle drawn, keep showing the rectangle
	if ((2==len(refPt)) and (not use_cropping)):
		cv2.rectangle(result, refPt[0], refPt[1], (255, 255, 0), 2)

	cv2.imshow('frame',sum)
	if (0!=source):
		video_out.write(result)
	# if there's a cropping rectangle drawn, keep showing the rectangle
	if ((2==len(refPt)) and (not use_cropping)):
		cv2.rectangle(result, refPt[0], refPt[1], (255, 255, 0), 2)



	key = cv2.waitKey(1) & 0xFF
	if ord('q') == key:
		break
	elif ord('d') == key:			# take & use difference image
		use_diff = True
		ref_img = img
	elif ord('e') == key:    		# add extra green to corners
		use_edges = not use_edges
	elif key == ord('t'): 			# toggle time-averaging
		use_time_avg = not use_time_avg
		avg1 = np.float32(img)
	elif key == ord('c'): # clear button
		print "already_pressed_clear = ",already_pressed_clear
		if (already_pressed_clear):
			use_diff = use_diff_save
			use_time_avg = use_time_avg_save
			use_denoise = use_denoise_save
			denoise_h = denoise_h_save
			thresh = thresh_save
			already_pressed_clear = False 
		else:
			use_diff_save = use_diff
			use_denoise_save = use_denoise
			use_time_avg_save = use_time_avg
			denoise_h_save = denoise_h
			thresh_save = thresh
			already_pressed_clear = True
			use_diff = False 
			use_time_avg = False
			use_denoise = False
			denoise_h = 10.0
			thresh = 13.0

	elif key == ord('n'): # toggle denoising (slow)
		use_denoise = not use_denoise
		if (use_denoise):
			denoise_h = 10.0
		else:
			denoise_h = 0.0
	elif (key == ord('k')) and (2==len(refPt)):  # cropping
		use_cropping = not use_cropping
		if (not use_cropping):
			ref_img = orig_ref
			green_img = orig_green
			avg1 = np.float32(ref_img)	 
	elif key == 0:  # up arrow
		thresh *= 1.1     # increase difference threshold = more green
	elif key == 1:  # down arrow
		thresh /= 1.1
	elif key == 2:  # left arrow
		denoise_h /= 1.1  # increase both denoising weight and kernel 
	elif key == 3:  # right arrow
		denoise_h *= 1.1



# Main Loop has finished, shutting down

if source != 0:				# close & release any output file
	video_out.release()
	video_out = None 

cap.release()				# release the camera
cv2.destroyAllWindows()
