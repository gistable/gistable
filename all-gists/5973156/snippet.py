from PIL import Image as pil
import urllib2
import numpy as np
source = "http://something"

req = urllib2.Request(source, headers={'User-Agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5"})
img_file = urllib2.urlopen(req)
im = StringIO(img_file.read()) # You can skip this and directly convert to numpy arrays
source = pil.open(im).convert("RGB")
_pilImage = source
npimg = np.fromstring(_pilImage.tostring(), dtype=np.uint8)
npimg = cv2.cvtColor(npimg, cv2.cv.CV_RGB2BGR)