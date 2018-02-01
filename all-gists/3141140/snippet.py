import Image
import sys
import glob

# Trim all png images with alpha in a folder
# Usage "python PNGAlphaTrim.py ../someFolder"

try:
	folderName = sys.argv[1]
except :
	print "Usage: python PNGPNGAlphaTrim.py ../someFolder"
	sys.exit(1)

filePaths = glob.glob(folderName + "/*.png") #search for all png images in the folder

for filePath in filePaths:
	image=Image.open(filePath)
	image.load()

	imageSize = image.size
	imageBox = image.getbbox()

	imageComponents = image.split()

	if len(imageComponents) < 4: continue #don't process images without alpha

	rgbImage = Image.new("RGB", imageSize, (0,0,0))
	rgbImage.paste(image, mask=imageComponents[3])
	croppedBox = rgbImage.getbbox()

	if imageBox != croppedBox:
		cropped=image.crop(croppedBox)
		print filePath, "Size:", imageSize, "New Size:",croppedBox
		cropped.save(filePath)