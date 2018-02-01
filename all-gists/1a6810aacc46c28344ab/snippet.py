import json
import sys
import os

print ".--=============--------------=============--."
print "|       Welcome to Image Matrix Maker!       |"
print ".--=============--------------=============--."

yeswords = ["yes", "y", "ya", "ok", "okay"]

try:
    from PIL import Image
except:
    ans = raw_input("The Python Image Library is required to continue. Install it now? ")
    if ans.lower() in yeswords:
        try:
            os.system("sudo easy_install pip")
            os.system("sudo pip install Pillow")
        except:
            print("Install failed. Make sure you have a working gcc compiler")
            exit()

try:
	sheet = sys.argv[1]
	print("| Using " + sheet)
except:
	sheet = raw_input("| Path to sprite sheet: ")

im = Image.open(sheet)
pix = im.load()

s = "int output[" + str(im.size[1]) + "][" + str(im.size[0]) + "] = { "
for zy in range(0, im.size[1]):
	s += "{ "
	for zx in range(0, im.size[0]):
		vals = pix[zx, zy]
		s += str(vals) + ", "
	s = s[:-2]
	s += " }, "
	
s = s[:-2] + " }"

print s
		

print ".--=============--=============--."
print "|           All Done!!           |"
print ".--=============--=============--."
