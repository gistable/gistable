#
#  sound_delay.py
#

"""
Record sound and play it back after a delay.
"""

import multiprocessing as mp
import time

CHUNK = 1024
CHANNELS = 1
RATE = 44100
DELAY_SECONDS = 5
DELAY_SIZE = DELAY_SECONDS * RATE / (10 * CHUNK)


def feed_queue(q):
    import pyaudio
    import numpy

    FORMAT = pyaudio.paInt16
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while True:
        frame = []
        for i in xrange(10):
            frame.append(stream.read(CHUNK))
        data_ar = numpy.fromstring(''.join(frame), 'int16')
        if q.full():
            q.get_nowait()
        q.put(data_ar)


queue = mp.Queue(maxsize=DELAY_SIZE)
p = mp.Process(target=feed_queue, args=(queue,))
p.start()

# give some time to bufer
time.sleep(DELAY_SECONDS)

import pygame.mixer
pygame.mixer.init()
S = pygame.mixer.Sound
while True:
    d = queue.get()
    S(d).play()