#!/usr/bin/python2

import sys

import numpy
from scipy.io import wavfile
from scipy.signal import fftconvolve

def usage():
    print >> sys.stderr, "Usage: wavgrep.py --like|--similar|--this needle.wav haystack.wav"
    sys.exit(2)

if len(sys.argv) != 4:
    usage()


if sys.argv[1] in ('--like', '--similar', '--this'):
    mode = sys.argv[1][2:]
else:
    usage()

needle_rate, needle = wavfile.read(sys.argv[2])
haystack_rate, haystack = wavfile.read(sys.argv[3])

if needle_rate != haystack_rate:
    print >> sys.stderr, "Sample rates are not the same"
    sys.exit(2)

if len(needle.shape) != 1:
    print >> sys.stderr, "Needle file is not mono"
    sys.exit(2)

if len(haystack.shape) != 1:
    print >> sys.stderr, "Haystack file is not mono"
    sys.exit(2)

if len(needle) == 0:
    print >> sys.stderr, "Needle is empty"
    sys.exit(2)

if len(needle) > len(haystack):
    print >> sys.stderr, "Needle is longer than haystack"
    sys.exit(2)

needle = numpy.array(needle, dtype=numpy.float64)
needle_len = len(needle)
haystack = numpy.array(haystack, dtype=numpy.float64)
haystack_len = len(haystack)

needle_norm = needle.dot(needle)

if needle_norm < 1000.0:
    print >> sys.stderr, "The needle is almost silent"
    sys.exit(2)

haystack_squared = numpy.hstack(([0.0], haystack * haystack))
haystack_cum_norm = numpy.cumsum(haystack_squared)
haystack_norm_at = haystack_cum_norm[needle_len:haystack_len + 1] - haystack_cum_norm[0:haystack_len + 1 - needle_len]

correlation_at = fftconvolve(haystack, needle[::-1], mode='valid')

difference_norm_at = haystack_norm_at + needle_norm - 2 * correlation_at

cos2phi_at = correlation_at * correlation_at / (haystack_norm_at + 0.000001) / needle_norm

gain_at = correlation_at / needle_norm
descaled_difference_norm_at = haystack_norm_at + needle_norm * gain_at * gain_at - 2 * gain_at * correlation_at

at = 0
if mode == 'like':
    at = numpy.argmax(correlation_at)
if mode == 'similar':
    at = numpy.argmax(cos2phi_at)
if mode == 'this':
    at = numpy.argmin(difference_norm_at)


print "The needle starts at sample: %d" % (at,)
print "Gain (dB): %3.2f" % (20.0 * numpy.log10(numpy.abs(gain_at[at]) + 0.000001),)
print "SNR (dB), treating gain change as noise: %3.2f" % (
    10.0 * numpy.log10(gain_at[at] * gain_at[at] * needle_norm / (difference_norm_at[at] + 0.000001)),)
print "SNR (dB), treating gain change as signal: %3.2f" % (
    10.0 * numpy.log10(gain_at[at] * gain_at[at] * needle_norm / (descaled_difference_norm_at[at] + 0.000001)),)

