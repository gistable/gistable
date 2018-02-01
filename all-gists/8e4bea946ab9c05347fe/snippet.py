# -*- coding: utf-8 -*-
 
import cv2
import numpy as np
 
print u'OpenCV Version:'+cv2.__version__
import sys
print u'Python Version:'+str(sys.version_info)
 
img = cv2.imread('./test_data/image000001.png')
gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
 
# @see http://answers.opencv.org/question/52130/300-python-cv2-module-cannot-find-siftsurforb/
# orb = cv2.ORB() <- it doesn't work
# orb = cv2.FeatureDetector_create('ORB') <- it doen't work
# ORB
e1_orb = cv2.getTickCount()
orb = cv2.ORB_create()
kp_orb = orb.detect(img, None)
kp_orb, des_orb = orb.compute(img, kp_orb)
e2_orb = cv2.getTickCount()
time_orb = (e2_orb-e1_orb)/cv2.getTickFrequency()
img_orb = cv2.drawKeypoints(gray, kp_orb, None)
 
# AKAZE
e1_akaze = cv2.getTickCount()
akaze = cv2.AKAZE_create()
kp_akaze = akaze.detect(img, None)
kp_akaze, des_akaze = akaze.compute(img, kp_akaze)
#img_akaze = cv2.drawKeypoints(gray, kp_akaze, None, color=(0, 255, 0))
e2_akaze = cv2.getTickCount()
time_akaze = (e2_akaze-e1_akaze)/cv2.getTickFrequency()
img_akaze = cv2.drawKeypoints(gray, kp_akaze, None)
 
# KAZE
e1_kaze = cv2.getTickCount()
kaze = cv2.KAZE_create()
kp_kaze = kaze.detect(img, None)
kp_kaze, des_kaze = kaze.compute(img, kp_kaze)
#img_kaze = cv2.drawKeypoints(gray, kp_kaze, None, color=(0, 255, 0))
e2_kaze = cv2.getTickCount()
time_kaze = (e2_kaze-e1_kaze)/cv2.getTickFrequency()
img_kaze = cv2.drawKeypoints(gray, kp_kaze, None)
 
# FAST
e1_fast = cv2.getTickCount()
fast = cv2.FastFeatureDetector_create()
kp_fast = fast.detect(img, None)
#kp_fast, des_fast = fast.compute(img, kp_fast)
e2_fast = cv2.getTickCount()
time_fast = (e2_fast-e1_fast)/cv2.getTickFrequency()
img_fast = cv2.drawKeypoints(gray, kp_fast, None)
 
# BRISK
e1_brisk = cv2.getTickCount()
brisk = cv2.BRISK_create()
kp_brisk = brisk.detect(img, None)
kp_brisk, des_brisk = brisk.compute(img, kp_brisk)
e2_brisk = cv2.getTickCount()
time_brisk = (e2_brisk-e1_brisk)/cv2.getTickFrequency()
img_brisk = cv2.drawKeypoints(gray, kp_brisk, None)
 
# MSER
#mser = cv2.MSER_create()
#img_mser = img.copy()
#regions = mser.detectRegions(gray, None)
#hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]
#cv2.polylines(img_mser, hulls, 1, (0, 255, 0))
orb_str = 'orb\t{0}\t{1}'.format(time_orb,time_orb/len(kp_orb))
akaze_str = 'akaze\t{0}\t{1}'.format(time_akaze,time_akaze/len(kp_akaze))
kaze_str = 'kaze\t{0}\t{1}'.format(time_kaze,time_kaze/len(kp_kaze))
fast_str = 'fast\t{0}\t{1}'.format(time_fast,time_fast/len(kp_fast))
brisk_str = 'brisk\t{0}\t{1}'.format(time_brisk,time_brisk/len(kp_brisk))
writebuffer = orb_str +'\n'+ akaze_str + '\n' + kaze_str +'\n'+ fast_str +'\n'+ brisk_str +'\n'
with open('./features_time.csv', 'a+') as f:
  f.write(writebuffer)

#cv2.imshow('ORB',img_orb)
#cv2.imshow('AKAZE', img_akaze)
#cv2.imshow('KAZE', img_kaze)
#cv2.imshow('FAST', img_fast)
#cv2.imshow('BRISK', img_brisk)
#cv2.imshow('MSER', img_mser)
#cv2.waitKey(0)