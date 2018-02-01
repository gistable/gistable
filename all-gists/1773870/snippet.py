#!/usr/bin/python

import wave
import numpy
import struct
import sys
import csv
from scikits.samplerate import resample

def write_wav(data, filename, framerate, amplitude):
    wavfile = wave.open(filename, "w")
    nchannels = 1
    sampwidth = 2
    framerate = framerate
    nframes = len(data)
    comptype = "NONE"
    compname = "not compressed"
    wavfile.setparams((nchannels,
                        sampwidth,
                        framerate,
                        nframes,
                        comptype,
                        compname))
    print("Please be patient whilst the file is written")
    frames = []
    for s in data:
        mul = int(s * amplitude)
        # print "s: %f mul: %d" % (s, mul)
        frames.append(struct.pack('h', mul))
    # frames = (struct.pack('h', int(s*self.amp)) for s in sine_list)
    frames = ''.join(frames)
    for x in xrange(0, 7200):
        wavfile.writeframes(frames)
    wavfile.close()
    print("%s written" %(filename))
    
    
if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "You must supply a filename to generate"
        exit(-1)
    for fname in sys.argv[1:]:
        data = []
        for time, value in csv.reader(open(fname, 'U'), delimiter=','):
            try:
                data.append(float(value))
            except ValueError:
                pass # Just skip it
        print "Generating wave file from %d samples" % (len(data),)
        arr = numpy.array(data)
        # Normalize data
        arr /= numpy.max(numpy.abs(data))
        filename_head, extension = fname.rsplit(".", 1)
        # Resample normalized data to 44.1 kHz
        target_samplerate = 44100
        sampled = resample(arr, target_samplerate/100000.0, 'sinc_best')
        write_wav(sampled, filename_head + ".wav", 100000, 32700)