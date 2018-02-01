import os
import scipy.io.wavfile as wav
# install lame
# install bleeding edge scipy (needs new cython)
fname = 'XC135672-Red-winged\ Blackbird1301.mp3'
oname = 'temp.wav'
cmd = 'lame --decode {0} {1}'.format( fname,oname )
os.system(cmd)
data = wav.read(oname)
# your code goes here
print len(data[1])
