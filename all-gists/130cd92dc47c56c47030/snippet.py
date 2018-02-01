from pydub import AudioSegment
from matplotlib import pyplot as plot
from PIL import Image, ImageDraw
import numpy as np
import os

src = "./test.mp3"

audio = AudioSegment.from_file(src)
data = np.fromstring(audio._data, np.int16)
fs = audio.frame_rate

BARS = 100
BAR_HEIGHT = 60
LINE_WIDTH = 5

length = len(data)
RATIO = length/BARS

count = 0
maximum_item = 0
max_array = []
highest_line = 0

for d in data:
	if count < RATIO:
		count = count + 1

		if abs(d) > maximum_item:
			maximum_item = abs(d)
	else:
		max_array.append(maximum_item)

		if maximum_item > highest_line:
			highest_line = maximum_item

		maximum_item = 0
		count = 1

line_ratio = highest_line/BAR_HEIGHT

im = Image.new('RGBA', (BARS * LINE_WIDTH, BAR_HEIGHT), (255, 255, 255, 1))
draw = ImageDraw.Draw(im)

current_x = 1
for item in max_array:
	item_height = item/line_ratio

	current_y = (BAR_HEIGHT - item_height)/2
	draw.line((current_x, current_y, current_x, current_y + item_height), fill=(169, 171, 172), width=4)

	current_x = current_x + LINE_WIDTH

im.show()


