#!/usr/bin/python

import sys


if len(sys.argv) < 2:
	print("Specify input file.")
	sys.exit(1)
INPUT = sys.argv[1]

input_x = 3840
input_y = 2160

screens_x = 5
screens_y = 4

res_x = 1280
res_y = 1024

output_x = screens_x * res_x
output_y = screens_y * res_y

scale = min(output_x / input_x, output_y / input_y)

pad_sides = output_x - input_x * scale
pad_top_bottom = output_y - input_y * scale

FFMPEG = "ffmpeg"
settings = "-c:v libx264 -crf 18"

#print(str(scale) + " " + str(pad_sides) + " " + str(pad_top_bottom))
# crop=100:100:12:34 will crop to 100x100 pixels at position 12, 34
# pad=640:480:0:40 will make video size to 640x480 with video placed at 0, 40
for y in range(screens_y):
	for x in range(screens_x):
		print("%s -i %s -vf scale=%f,pad=%d:%d:%d:%d,crop=%d:%d:%d:%d %s %s" % (FFMPEG, INPUT, scale, output_x, output_y, int(pad_sides/2), int(pad_top_bottom/2), res_x, res_y, res_x * x, res_y * y, settings, (str(x) + str(y) + ".mp4")))