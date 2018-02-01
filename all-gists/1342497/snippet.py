# Copyright (c) 2011, Eng Eder de Souza
#    ___    _              _       ___
#   | __|__| |___ _ _   __| |___  / __| ___ _  _ _____ _
#   | _|/ _` / -_) '_| / _` / -_) \__ \/ _ \ || |_ / _` |
#   |___\__,_\___|_|   \__,_\___| |___/\___/\_,_/__\__,_|
#Accessing the Google API for speech recognition!
#Open a file type Wav to speech recognition
#This source does not require any external programs to perform audio conversions :-)
#http://ederwander.wordpress.com/2011/11/06/accessing-the-google-speech-api-python/
#Eng Eder de Souza
#date 01/11/2011

from scikits.samplerate import resample
from tempfile import mkstemp
from os import remove
import scikits.audiolab as audiolab
# if you want make the down sample rate using scipy.signal
#import scipy.signal
import urllib2
import sys

if len(sys.argv)<2 :
        print 'Usage: %s <audio file.wav>' %sys.argv[0]
        sys.exit(0)
File=sys.argv[1]

#making a file temp for manipulation
cd, FileNameTmp    = mkstemp('TmpSpeechFile.flac')

#Frame Rate used by api speech from google
fr=16000.

#using audiolab to read wav file
Signal, fs = audiolab.wavread(File)[:2]

#changing the original sample rate to 16000fs fast mode
Signal = resample(Signal, fr/float(fs), 'sinc_best')

#changing sample rate from audio file using scipy this is a bit slow
#Signal=scipy.signal.resample(Signal,int(round(len(Getsignal)*fr)/float(fs)),window=None)

# file Format type
fmt         = audiolab.Format('flac', 'pcm16')
nchannels   = 1

# making the file .flac
afile =  audiolab.Sndfile(FileNameTmp, 'w', fmt, nchannels, fr)

#writing in the file
afile.write_frames(Signal)

#Sending to google the file .flac
url = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=pt-BR"
flac=open(FileNameTmp,"rb").read()
header = {'Content-Type' : 'audio/x-flac; rate=16000'}
req = urllib2.Request(url, flac, header)
data = urllib2.urlopen(req)
print data.read()
remove(FileNameTmp)
