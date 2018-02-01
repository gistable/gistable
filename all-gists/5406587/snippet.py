from SimpleCV import Image, Color, Display

# Make a function that does a half and half image.
def halfsies(left,right): 
    result = left
    # crop the right image to be just the right side.
    crop   = right.crop(right.width/2.0,0,right.width/2.0,right.height)
    # now paste the crop on the left image.
    result = result.blit(crop,(left.width/2,0))
    # return the results.
    return result
# Load an image from imgur.
img = Image('http://i.imgur.com/lfAeZ4n.png')
# binarize the image using a threshold of 90 
# and invert the results.
output = img.binarize(90).invert()
# create the side by side image.
result = halfsies(img,output)
# show the resulting image.
result.show()
# save the results to a file. 
result.save('juniperbinary.png')