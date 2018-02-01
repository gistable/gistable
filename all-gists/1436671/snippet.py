'''
A hack based on this http://mikepultz.com/2011/03/accessing-google-speech-api-chrome-11/. While with smaller voice samples google speech to text works really good, as length increases quality decreases. So here using audiolab and numPy we are breaking audio sample, in smaller chunks, and removing blank/empty spaces from audio signal and then pushing them to google for processing. 
It takes wav file format as input but can be changed to other formats too.
'''

from scikits.audiolab import wavread, play, flacwrite
from numpy import average, array, hstack
import os
import sys

if len(sys.argv) != 2:
    print 'usage speech2text.py filename'
    exit(1)

buff, fs, bp = wavread(sys.argv[1])
a_buff = abs(buff)
window = 1000

# To get all index values of slots where we have some sound
index = array([i for i in range((len(buff)/window) + 1) if average(a_buff[i*window:(i+1)*window]) > average(a_buff)/2])
start = index[hstack((True, index[1:] - index[:-1] > 10))] * window
end = index[hstack((index[1:] - index[:-1] > 10, True))] * window
print start
print end
for i in range(len(start)):
    flacwrite(buff[start[i]:end[i]], 'part.flac', fs)
    os.system('wget --post-file part.flac --header="Content-Type: audio/x-flac; rate=22050" -O "blah" "http://www.google.com/speech-api/v1/recognize?lang=en-us&client=chromium"')
    # play(buff[start[i]:end[i]], fs)
    print open('blah').read()
