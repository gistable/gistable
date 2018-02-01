#!/usr/bin/python

import numpy
import pyaudio
import re
import sys

WIDTH = 79
BOOST = 1.0


# Create a nice output gradient using ANSI escape sequences.
cols = [30, 34, 35, 91, 93, 97]
chars = [(' ', False), (':', False), ('%', False), ('#', False),
         ('#', True), ('%', True), (':', True)]
gradient = []
for bg, fg in zip(cols, cols[1:]):
    for char, invert in chars:
        if invert:
            bg, fg = fg, bg
        gradient.append('\x1b[{};{}m{}'.format(fg, bg + 10, char))


class Spectrogram(object):
    def __init__(self):
        self.audio = pyaudio.PyAudio()

    def __enter__(self):
        """Open the microphone stream."""
        device_index = self.find_input_device()
        device_info = self.audio.get_device_info_by_index(device_index)
        rate = int(device_info['defaultSampleRate'])

        self.buffer_size = int(rate * 0.02)
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1, rate=rate, input=True,
                                      input_device_index=device_index,
                                      frames_per_buffer=self.buffer_size)
        return self

    def __exit__(self, *ignored):
        """Close the microphone stream."""
        self.stream.close()

    def find_input_device(self):
        """
        Find a microphone input device. Return None if no preferred
        deveice was found, and the default should be used.
        """
        for i in range(self.audio.get_device_count()):
            name = self.audio.get_device_info_by_index(i)['name']
            if re.match('mic|input', name, re.I):
                return i
        return None

    def color(self, x):
        """
        Given 0 <= x <= 1 (input is clamped), return a string of ANSI
        escape sequences representing a gradient color.
        """
        x = max(0.0, min(1.0, x))
        return gradient[int(x * (len(gradient) - 1))]

    def listen(self):
        """Listen for one buffer of audio and print a gradient."""
        block_string = self.stream.read(self.buffer_size)
        block = numpy.fromstring(block_string, dtype='h') / 32768.0
        nbands = 30 * WIDTH
        fft = abs(numpy.fft.fft(block, n=nbands))

        pos, neg = numpy.split(fft, 2)
        bands = (pos + neg[::-1]) / float(nbands) * BOOST
        line = (self.color(x) for x in bands[:WIDTH])
        print ''.join(line) + '\x1b[0m'
        sys.stdout.flush()

if __name__ == '__main__':
    with Spectrogram() as s:
        while True:
            s.listen()
