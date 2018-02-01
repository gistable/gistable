import PIL
from PIL import Image, ImageOps

def resizecrop(src, out, width, height):
	img = Image.open(src)
	img = ImageOps.fit(img, (width, height), Image.ANTIALIAS, 0, (0.5, 0.5))
	img.save(out)