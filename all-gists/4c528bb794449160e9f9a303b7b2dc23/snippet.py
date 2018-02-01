#!/usr/bin/env python

import pytesseract
import Image
import cv2

# some func
def click_prt_pix_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print('pixel(%d, %d) color is %s' % (x, y, img[y, x]))


# some vars
# /dev/video1
cap = cv2.VideoCapture(1)

while True:
    ret, img = cap.read()
    
    # skip if no image
    if img is None:
        break
    
    # restrain image to value area [startY:endY, startX:endX]
    img = img[215:254, 340:400]
    
    # blur image
    img = cv2.blur(img,(1,1))
    
    # show image
    cv2.imshow('i', img)
    cv2.setMouseCallback('i', click_prt_pix_color)
    
    # OCR decode with tesseract
    index_str = pytesseract.image_to_string(Image.fromarray(img), config='outputbase digits')
    
    # check index and use it...
    if index_str.isdigit():
        index = int(index_str)
        print('OCR result is %d' % index)

    # end of main loop if 'esc' press
    key = cv2.waitKey(100)
    if key & 0x0f == 0x0b:
        break

cv2.destroyAllWindows()