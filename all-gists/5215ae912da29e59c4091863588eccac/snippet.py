import cv2
import urllib.request

# Will use matplotlib for showing the image
from matplotlib import pyplot as plt

# Plot inline
%matplotlib inline

# For local images, read as usual
# img = cv2.imread("opencv-logo2.png")

# For remote, use urllib, as per "http://stackoverflow.com/questions/21061814"
req = urllib.request.urlopen("http://cloudcv.org/static/img/opencv.jpg")

arr = np.asarray(bytearray(req.read()), dtype=np.uint8)

img = cv2.imdecode(arr,-1)

# The important part - Correct BGR to RGB channel
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Plot
plt.imshow(img)