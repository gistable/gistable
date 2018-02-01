import array
import smc.freeimage as fi
from PIL import Image
import numpy as np
import cv2

def gamma_correction(a, gamma):
	return np.power(a, 1/gamma)

def load_hdr(file):
	img = fi.Image(file).flipVertical()

	size = img.height * img.pitch
	raw = img.getRaw()
	floats = array.array('f', raw)

	a1 = np.array(floats).reshape((img.width, img.height, 3))
	a2 = np.clip(gamma_correction(a1, 2.2), 0, 1)
	return (a2 * 255).astype(np.uint8)

def save_image(file, image):
	img2 = Image.fromarray(image)
	img2.save(file)

def main():
	image = load_hdr('grace_probe.hdr')
	save_image('grace_probe.png', image)
	cv2.imshow('grace_probe', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
	cv2.waitKey(0)
	cv2.destroyAllWindows()

if __name__ == '__main__':
	main()
