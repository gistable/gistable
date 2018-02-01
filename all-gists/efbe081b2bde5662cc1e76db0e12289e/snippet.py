import cv2

def diff(img,img1): # returns just the difference of the two images
  return cv2.absdiff(img,img1)
  
def diff_remove_bg(img0,img,img1): # removes the background but requires three images 
  d1 = diff(img0,img)
  d2 = diff(img,img1)
  return cv2.bitwise_and(d1,d2)