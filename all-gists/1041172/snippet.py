import sys
from PIL import Image
from gameduino import prep


image_path = ""
h_name = ""

# retrieve the command line arguments
if (len(sys.argv) > 2):
	image_path = sys.argv[1]
	sprite_name = sys.argv[2]
else:
	print "Not all commands entered"
	sys.exit(0)

# create the header file
hdr = open(sprite_name+".h", "w")
ir = prep.ImageRAM(hdr)

im = Image.open(image_path)

# show the image to be changed
im.show()

sprite = prep.palettize(im, 4)

# dump to a h file
prep.dump(hdr, sprite_name+"_palette", sprite)
ir.addsprites(sprite_name, (16,16), sprite, prep.PALETTE4A)