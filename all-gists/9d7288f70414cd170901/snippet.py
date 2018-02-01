#! /usr/bin/env python3
'''(1.196 x STE at 60 ms after the J-point in V3 in mm) + (0.059 x computerized QTc) - (0.326 x R-wave Amplitude in V4 in mm).
Use the calculator below. A value greater than 23.4 is quite sensitive and specific for LAD occlusion.
http://hqmeded-ecg.blogspot.com/2013/06/here-is-link-to-full-text-of-article-in.html'''

import sys
try:
    import console
    ios = True
except ImportError:
    ios = False

ste, qtc, rwave = [float(each) for each in sys.argv[1:]]

score = (1.196 * ste + 0.059 * qtc - 0.326 * rwave) - 23.4

score_string = 'Score: {}'.format(score)
score_message = 'Positive scores are sensitive and specific for LAD occlusion.'

if ios:
    console.alert(score_string, score_message)
else:
    print(score_string, '\n', score_message)

