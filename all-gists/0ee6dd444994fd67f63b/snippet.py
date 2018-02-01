import skimage; 
from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label
from skimage.morphology import closing, square
from skimage.measure import regionprops
from skimage.color import label2rgb
import cv2
import numpy as np
import sys



if __name__ == '__main__':
	print(skimage.__version__)
	img = data.imread("garden1.jpg", 1)
	# img = data.imread("garden2.jpg", 1)
	print type(img), img.shape, type(img[0][0])
	thresh = threshold_otsu(img)
	bw = closing(img > thresh, square(1))
	cleared = bw.copy()
	clear_border(cleared)
	
	# label image regions
	label_image = label(cleared)
	borders = np.logical_xor(bw, cleared)
	label_image[borders] = -1
	colors = np.random.rand(300, 3);
	background = np.random.rand(3);
	image_label_overlay = label2rgb(label_image, image=img, colors=colors, bg_color=background)
	cv2.imwrite('Done.png',image_label_overlay*255)