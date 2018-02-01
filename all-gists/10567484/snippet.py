# This line imports the modules we will need. The first is the sys module used
# to read the command line arguments. Second the Python Imaging Library to read
# the image and third numpy, a linear algebra/vector/matrix module.
import sys; from PIL import Image; import numpy as np

# This is a list of characters from low to high "blackness" in order to map the
# intensities of the image to ascii characters 
chars = np.asarray(list(' .,:;irsXA253hMHGS#9B&@'))
 
# Check whether all necessary command line arguments were given, if not exit and show a
# usage hint. Since the original comment will also be counted as argument we need 4.
if len(sys.argv) != 4: print( 'Usage: ./asciinator.py image scale factor' ); sys.exit()

# Get some important constants like the filename f, the image size scaling SC and a
# intensity correction factor from the command line arguments. The WCF is a width correction
# factor we will use since most font characters are higher than wide. 
f, SC, GCF, WCF = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), 7/4

# This line opens the image 
img = Image.open(f)

# here we set the new size of the image. The whole image is scaled by the scale factor given
# in the command line arguments and we also correct the image with the width correction factor
# so that the resulting asciii image has approximately the same aspect ratio as the original
# image.
S = ( round(img.size[0]*SC*WCF), round(img.size[1]*SC) )

# Here we resize the image and add up the rgb values of the image to get the overall intensity
# values for each pixel.
img = np.sum( np.asarray( img.resize(S) ), axis=2)

# Here we scale the smallest intensity value to zero
img -= img.min()
# We divide the intensity values by it maximum so all intensities are now between 0 and 1. We invert
# the intensity scale by subtracting it from one, so that the whitest pixels map to the space character
# and the darkest pixels to the @ character. The now scaled intensities are now raised to the power of the
# intensity correction factor GCF which alters the intensity histogram of the image and, thus, gives some
# some freedom to counteract very dark or light images. A CGF of 1 gives the original pixel intensities. 
# Finally the scaled intensities are multiplied with the biggest index of the character array chars (n-1)
# and, later, truncated to int which basically maps every intensity value of the original image to an index 
# of the ascii character array. 
img = (1.0 - img/img.max())**GCF*(chars.size-1)
 
# Here we assemble and print our ascii art. The image is truncated to int and the entire image matrix is passed
# as an index to the character array. This is possible because numpy actually allows indices to be vectors or matrices
# where the output will have the same dimensions of the matrix "filtered" by the indexed vector. For example, if
#
#
#     v = array(['a', 'b', 'c', 'd']) and M = array( [[0, 1],     it follows that v[M] = [['a', 'b'],  
#                                                     [2, 3]] )                           ['c', 'd']]
#
# In the inner generator we combine the characters of each row (r) of the now ascii-mapped image to a single string
# and in the outer join we combine all of the row characters by gluing them with together with newline characters.
# All of that is printed and done :) 
print( "\n".join( ("".join(r) for r in chars[img.astype(int)]) ) )