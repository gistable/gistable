#!/usr/bin/env python
#encoding=utf-8
 
# Convert image to Pwmout grayscale data for dot-matrix LED
# Input image format can be JPEG, PNG etc

from PIL import Image
import sys

if __name__ == "__main__":
    argvs = sys.argv
    argc = len(argvs)
    if (argc != 2):
        print 'Usage: # python %s filename' % argvs[0]
        quit()

    im = Image.open(argvs[1])
    pix = im.load()

    print "const float img[", im.size[0], "][", im.size[1], "] = {"
    for y in range(0, im.size[1]):
        for x in range(0, im.size[0]):
            # conver RGB to grayscale
            gray = (0.299 * pix[x,y][0] + 0.587 * pix[x,y][1] + 0.114 * pix[x,y][2])
            print ((255-gray)/256), ","
    print "};"
