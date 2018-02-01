#!/usr/bin/python

import cv2
import numpy as np
import wave
import struct
import sys

# usage instructions:
# ./image2spectrogram.py input.png
# sox output.wav -n spectrogram -m -o output.png

image = cv2.imread(sys.argv[1], flags=cv2.CV_LOAD_IMAGE_GRAYSCALE)
height, width = image.shape
samples = []

for i in range(0, width):
    column = image[:, i]
    flipped = np.flipud(column)
    window = np.hstack((flipped[:-1], column))
    # FIXME need to check range of np.real(), should be [-2**7,+2**7)
    ifft = np.int32(2**16 + 2**23 * np.real(np.fft.ifft(window)))
    for sample in ifft:
        samples.append(struct.pack('i', sample))

output = wave.open('output.wav', 'w')
output.setparams((1, 4, 44100, 0, 'NONE', 'not compressed'))
output.writeframes(''.join(samples))
output.close()