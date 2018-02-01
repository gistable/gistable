import sys
import numpy as np
import scipy.ndimage as nd
from scipy.cluster.vq import vq
from scipy.misc import imsave

def crayola_9():
    """
    Palette of the first 8 crayola colors + white
    """
    palette = []
    palette.append([0,0,0])
    palette.append([31, 117, 254])
    palette.append([180, 103, 77])
    palette.append([28, 172, 120])
    palette.append([255, 117, 56])
    palette.append([238, 32 ,77 ])
    palette.append([146, 110, 174])
    palette.append([252, 232, 131])
    palette.append([255, 255, 255])
    return np.array(palette)  
  
def quantize(fname, palette):
    """
    quantize an image with a given color palette
    """
    
    # read image and resize
    img = nd.imread(fname)
    
    # reshape to array of points
    pixels = np.reshape(img, (img.shape[0] * img.shape[1], 3))
    
    # quantize
    qnt, _ = vq(pixels, palette)
    
    # reshape back to image
    centers_idx = np.reshape(qnt, (img.shape[0], img.shape[1])) 
    clustered = palette[centers_idx]
    
    # return quantized image and histogram
    return clustered

if __name__ == '__main__':

    # get filename
    fname = sys.argv[1]
    
    # quantize single file
    result = quantize(fname, crayola_9())
    
    # save resulting image
    imsave('output.png', result)
  