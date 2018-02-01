#Copyright (c) 2012 Vipin Nair <swvist@gmail.com>

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


#Change the values according to your requirement.
#The generated image will be named 'output' and will be in IMAGES_DIRECTORY
#after the execution of the script

IMAGES_DIRECTORY	=	'/home/swvist/pics/'
ROW_IMAGE_COUNT		=	21
COLUMN_IMAGE_COUNT	=	27
IMAGE_DIMENSION		=	{ "height" : 50, "width" : 50}


#You need not modify anything below this line.

import os
import Image
import random


#Generates a list with absolute path of all the images in thr IMAGES_DIRECTORY
piclist = [os.path.join(IMAGES_DIRECTORY,pic) for pic in os.listdir(IMAGES_DIRECTORY)]

#Stores the Image Count
piccount = len(piclist)

#Shuffles the Image List (piclist)
random.shuffle(piclist)

#Creates a new image canvas, on which the image tiles will be placed.
out = Image.new("L",(IMAGE_DIMENSION["width"]*COLUMN_IMAGE_COUNT,IMAGE_DIMENSION["height"]*ROW_IMAGE_COUNT))

#Creates the tiles one by one in a linear fashion
counter=0
for i in range(ROW_IMAGE_COUNT):
	for j in range(COLUMN_IMAGE_COUNT):
		counter += 1
		if counter < piccount :
			print counter
			out.paste(Image.open(piclist[counter]),(j*IMAGE_DIMENSION["width"],i*IMAGE_DIMENSION["height"]))
		else:
			break
#Saves the image in IMAGES_DIRECTORY with name output
out.save(IMAGES_DIRECTORY+"output","JPEG")