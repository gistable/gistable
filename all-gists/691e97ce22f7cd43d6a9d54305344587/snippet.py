"""
Problem:
  How to Convert PDF to Image with Python Script ?

Installation:
  I use ubuntu OS 14.04
  We use wrapper for ImageMagick [http://www.imagemagick.org/script/index.php] to Convert The PDF file
  in Python do: 
    
  $ sudo apt-get install libmagickwand-dev
  $ pip install Wand
  
  now install PIL 
  $ pip install Pillow

  More Installation http://sorry-wand.readthedocs.org/en/latest/guide/install.html
  more about wand https://pypi.python.org/pypi/Wand
"""

from PIL import Image as Img
from wand.image import Image
import uuid
import numpy as np
import glob
import os
import sys

def convert(filepdf):
    #used to generate temp file name. so we will not duplicate or replace anything
    uuid_set = str(uuid.uuid4().fields[-1])[:5]
    try:
        #now lets convert the PDF to Image
        #this is good resolution As far as I know
        with Image(filename=filepdf, resolution=200) as img:
            #keep good quality
            img.compression_quality = 80
            #save it to tmp name
            img.save(filename="temp/temp%s.jpg" % uuid_set)
    except Exception, err:
        #always keep track the error until the code has been clean
        #print err
        return False
    else:
        """
        We finally success to convert pdf to image. 
        but image is not join by it self when we convert pdf files to image. 
        now we need to merge all file
        """
        pathsave = []
        try:
            #search all image in temp path. file name ends with uuid_set value
            list_im = glob.glob("temp/temp%s*.jpg" % uuid_set)
            list_im.sort() #sort the file before joining it
            imgs = [Img.open(i) for i in list_im]
            #now lets Combine several images vertically with Python
            min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
            imgs_comb = np.vstack(
                (np.asarray(i.resize(min_shape)) for i in imgs))
            # for horizontally  change the vstack to hstack
            imgs_comb = Img.fromarray(imgs_comb)
            pathsave = "MyPdf%s.jpg" % uuid_set
            #now save the image
            imgs_comb.save(pathsave)
            #and then remove all temp image
            for i in list_im:
                os.remove(i)
        except Exception, err:
            #print err 
            return False
        return pathsave

if __name__ == "__main__":
     arg = sys.argv[1]
     result = convert(arg)
     if result:
        print "[*] Succces convert %s and save it to %s" % (arg, result)
     else:
        print "[!] Whoops. something wrong dude. enable err var to track it"

"""
===========================================
Running Test:
  python testing-pdf.py zz.pdf
  [*] Succces convert zz.pdf and save it to Resume63245.jpg
  
===========================================
"""
#well I hope this will be useful for you & others.       