#Import both skimage and cv
from skimage import transform as tf
from skimage import io
import cv2

import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

# Could use either skimage or cv to read the image
# img = io.imread('jar.png')   
img = cv2.imread('jar.png')
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray_image,127,255,cv2.THRESH_BINARY)
edges = cv2.Canny(thresh ,100, 200)

# Find largest contour (should be the label)
contours,hierarchy = cv2.findContours(edges, 0, 1)
areas = [cv2.contourArea(c) for c in contours]
max_index = np.argmax(areas)
cnt=contours[max_index]

# Create a mask of the label
mask = np.zeros(img.shape,np.uint8)
cv2.drawContours(mask, [cnt],0,255,-1)

# Find the 4 borders
scale = 1
delta = 0
ddepth = cv2.CV_8U
borderType=cv2.BORDER_DEFAULT
left = cv2.Sobel(mask,ddepth,1,0,ksize=1,scale=1,delta=0,borderType=borderType)
right = cv2.Sobel(mask,ddepth,1,0,ksize=1,scale=-1,delta=0, borderType=borderType)
top = cv2.Sobel(mask,ddepth,0,1,ksize=1,scale=1,delta=0,borderType=borderType)
bottom = cv2.Sobel(mask,ddepth,0,1,ksize=1,scale=-1,delta=0,borderType=borderType)

# Remove noise from borders
kernel = np.ones((2,2),np.uint8)
left_border = cv2.erode(left,kernel,iterations = 1)
right_border = cv2.erode(right,kernel,iterations = 1)
top_border = cv2.erode(top,kernel,iterations = 1)
bottom_border = cv2.erode(bottom,kernel,iterations = 1)

# Equations 1 and 2: c1 + c2*x + c3*y + c4*x*y, c5 + c6*y + c7*x + c8*x^2
# Find coeficients c1,c2,c3,c4,c5,c6,c7,c8 by minimizing the error function. 
# Points on the left border should be mapped to (0,anything).
# Points on the right border should be mapped to (108,anything)
# Points on the top border should be mapped to (anything,0)
# Points on the bottom border should be mapped to (anything,70)
sum_of_squares_y = '+'.join( [ "(c[0]+c[1]*%s+c[2]*%s+c[3]*%s*%s)**2" % \
    (x,y,x,y) for y,x,z in np.transpose(np.nonzero(left_border)) ])
sum_of_squares_y += " + "
sum_of_squares_y += '+'.join( [ "(-108+c[0]+c[1]*%s+c[2]*%s+c[3]*%s*%s)**2" % \
    (x,y,x,y) for y,x,z in np.transpose(np.nonzero(right_border)) ])
res_y = optimize.minimize(lambda c: eval(sum_of_squares_y),(0,0,0,0),method='SLSQP')

sum_of_squares_x = '+'.join( [ "(-70+c[0]+c[1]*%s+c[2]*%s+c[3]*%s*%s)**2" % \
    (y,x,x,x) for y,x,z in np.transpose(np.nonzero(bottom_border)) ] )
sum_of_squares_x += " + "
sum_of_squares_x += '+'.join( [ "(c[0]+c[1]*%s+c[2]*%s+c[3]*%s*%s)**2" % \
    (y,x,x,x) for y,x,z in np.transpose(np.nonzero(top_border)) ] )
res_x = optimize.minimize(lambda c: eval(sum_of_squares_x),(0,0,0,0), method='SLSQP')

# Map the image using equatinos 1 and 2 (coeficients c1...c8 in res_x and res_y)
def map_x(res, coord):
    return res[0] + res[1]*coord[1] + res[2]*coord[0] + res[3]*coord[1]*coord[0]
def map_y(res, coord):
    return res[0] + res[1]*coord[0] + res[2]*coord[1] + res[3]*coord[1]*coord[1]

flattened = np.zeros(img.shape, img.dtype) 
for y,x,z in np.transpose(np.nonzero(mask)):
    new_y = map_y(res_x.x,[y,x]) 
    new_x = map_x(res_y.x,[y,x])
    flattened[float(new_y)][float(new_x)] = img[y][x]
# Crop the image 
flattened = flattened[0:70, 0:105]

# Alternatively, use PiecewiseAffineTransform from SciKit-image to transform the image
leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])

dst = list()
src = list()
for y,x,z in np.transpose(np.nonzero(top_border)):
    dst.append([x,y])
    src.append([x,topmost[1]])
for y,x,z in np.transpose(np.nonzero(bottom_border)):
    dst.append([x,y])
    src.append([x,bottommost[1]])
for y,x,z in np.transpose(np.nonzero(left_border)):
    dst.append([x,y])
    src.append([leftmost[0],y])
for y,x,z in np.transpose(np.nonzero(right_border)):
    dst.append([x,y])
    src.append([rightmost[0],y])
src = np.array(src)
dst = np.array(dst)

tform3 = tf.PiecewiseAffineTransform()
tform3.estimate(src, dst)
warped = tf.warp(img, tform3, order=2)
warped = warped[85:170, 31:138]