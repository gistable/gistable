import scipy
import numpy as np
from scipy.ndimage import imread
from scipy.io import wavfile
from scipy.signal import resample_poly
from sys import argv

"""
  Usage: ./fakenapt.py <in.png> <out.wav>
  The input PNG should be 909 pixels wide.
"""

DATA_RATE = 4160
CARRIER = 2400

SYNC_HIGH = 244
SYNC_LOW = 11

WEDGE = [31, 63, 95, 127, 159, 191, 223, 255]
SYNC_A = [SYNC_LOW] * 4 + [SYNC_HIGH, SYNC_HIGH, SYNC_LOW, SYNC_LOW] * 7 + [SYNC_LOW] * 7
SYNC_B = [SYNC_LOW] * 4 + [SYNC_HIGH, SYNC_HIGH, SYNC_HIGH, SYNC_LOW, SYNC_LOW] * 7
SPACE_VIS = [SYNC_LOW] * 47
SPACE_IR = [SYNC_HIGH] * 47
MINUTE_BLACK = [0] * 47
MINUTE_WHITE = [255] * 47

TELEMETRY_PLACEHOLDER = WEDGE + [0, 55, 59, 63, 67, 63, 15, 0]


def apt_line(line_number, first_row, second_row, telemetry):
    minute_modulo = line_number % 120
    telemetry_wedge = (line_number % 128) // 8

    space = SPACE_VIS
    telemetry[15] = WEDGE[1]

    if minute_modulo < 2:
        space = MINUTE_BLACK

    elif minute_modulo < 4:
        space = MINUTE_WHITE

    line = np.concatenate((SYNC_A, space, first_row, [telemetry[telemetry_wedge]] * 45))

    space = SPACE_IR
    telemetry[15] = WEDGE[3]

    if minute_modulo < 2:
        space = MINUTE_BLACK

    elif minute_modulo < 4:
        space = MINUTE_WHITE

    line = np.concatenate((line, SYNC_B,  space,  second_row, [telemetry[telemetry_wedge]] * 45))

    return np.double(line)

image = np.uint8(imread(argv[1], "L"))


i = 0
samples = []

for line in range(image.shape[0]):
    data = apt_line(line, image[line], image[line], TELEMETRY_PLACEHOLDER)
    data = scipy.signal.resample_poly(data, 8, 1, window="boxcar")
    data /= 255.0

    for value in data:
        value = -1 + value*2
        samples.append(np.sin(i * CARRIER * np.pi * 2 / (DATA_RATE*8)) * (1 + value * 0.87) * 0.5)
        i += 1

    if line % 100 == 0:
        print(line)

scipy.io.wavfile.write(argv[2], 11025, (scipy.signal.resample_poly(samples, 11025, DATA_RATE * 8, window="boxcar") * 32767)
                       .astype(np.int16))