#Eng Eder de Souza 01/12/2011
#Speech Recognizer prototype ...
#Real time VAD implementation using Google Speech Api

from tempfile import mkstemp
from subprocess import call
from os import remove, listdir
from matplotlib.mlab import find
import pyaudio
import numpy as np
import wave
import math
import struct
import urllib2
import sys
import re


#For Portuguese Brazilian Speech Recognizer!
Lang="pt-BR"

#or for English Speech Recognizer
#Lang="en-US"

#Download the Binary Windows File to flac conversor Here:
#http://sourceforge.net/projects/flac/files/flac-win/flac-1.2.1-win/
#where are your flac.exe ???
FlacLocal="flac.exe"

url = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang='+Lang

cd, FileNameTmp = mkstemp('TmpSpeechFile.flac')

TmpLocation=FileNameTmp.rsplit("\\", 1)[0] + "\\"


#http://en.wikipedia.org/wiki/Vocal_range
#Assuming Vocal Range Frequency upper than 80 Hz
VocalRange = 80.0

#Assuming Energy threshold upper than 30 dB
Threshold = 30

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2
Max_Seconds = 10
TimeoutSignal=((RATE / chunk * Max_Seconds) + 2)
NoSpeaking_seconds = 1;
Timeout_NoSpeaking=(RATE / chunk * NoSpeaking_seconds + 2)
silence = True
Time=0



def rmOldFiles(TmpLocation):
	ext=".flac"
	for fname in listdir(TmpLocation):
    		if fname[-len(ext):] == ext :
			if fname != FileNameTmp.rsplit("\\", 1)[1]:
				rmFile=TmpLocation + fname
				remove(rmFile)

def SendSpeech(File):
	#print File
	flac=open(File,"rb").read()
	#print flac
	header = {'Content-Type' : 'audio/x-flac; rate=16000'}
	req = urllib2.Request(url, flac, header)
	data = urllib2.urlopen(req)
	print "You Said ..."
	#print data.read()
	find = re.findall('"utterance":(.*),', data.read())
	#utterance
	#remove(FileNameTmp)
	#print find
	try:
		print find[0]
	except:
		print "speech not recognized ..." 

def GetStream(chunk):
	return stream.read(chunk)

def Pitch(signal):
	signal = np.fromstring(signal, 'Int16');
	crossing = [math.copysign(1.0, s) for s in signal]
	index = find(np.diff(crossing));
	f0=round(len(index) *RATE /(2*np.prod(len(signal))))
	return f0;

def rms(frame):
	count = len(frame)/swidth
    	format = "%dh"%(count)
    	shorts = struct.unpack( format, frame )

    	sum_squares = 0.0
    	for sample in shorts:
        	n = sample * SHORT_NORMALIZE
        	sum_squares += n*n
		rms = math.pow(sum_squares/count,0.5);

	return rms * 1000

def speaking(data):
	rms_value = rms(data) 
	if rms_value > Threshold:
		return True
	else:
		return False

def WriteSpeech(WriteData):
	stream.stop_stream()
	stream.close()
	p.terminate()
	wf = wave.open(FileNameTmp, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(WriteData)
	wf.close()

def EndRecord():
	
	#########print FileNameTmp
	File= TmpLocation + "eder22.flac"
	##########print File

	str_Flac = FlacLocal + " -s -f " + FileNameTmp + " -o " + File
	##########print str_Flac
	proc=call(str_Flac, shell=False)
	SendSpeech(File)
	remove(File)
	#remove(FileNameTmp)

def VAD(SumFrequency, data2):
	AVGFrequency = SumFrequency/(Timeout_NoSpeaking+1);
	#if AVGFrequency > VocalRange:
	if AVGFrequency > VocalRange/2:
		S=speaking(data2)
		if S:
			return True;
		else: 
			return False;

		
	else:
		#S=speaking(data2)
		#if S:
			#Speech=True;
		#else: 
		return False;

def RecordSpeech(TimeoutSignal, LastBlock):
	
	SumFrequency=0;
	test=Timeout_NoSpeaking;
	all.append(LastBlock)
	for i in range(0, TimeoutSignal):
		try:
			data = GetStream(chunk)
		except:
			continue

		######print Pitch(data);
		SumFrequency = Pitch(data)+SumFrequency;
    		all.append(data)
    		stream.write(data, chunk)
		data2 = ''.join(all)

		if i == test:
			#Speech=speaking(data2)
			test = test + Timeout_NoSpeaking
			Speech=VAD(SumFrequency, data2);
			SumFrequency=0;
			if Speech:
				
				#test = test + Timeout_NoSpeaking
				data2 = ''
			else:
				data = ''.join(all)
				WriteSpeech(data)
				EndRecord()
				sys.exit()
	print "Send after timeout";
	data = ''.join(all)
	WriteSpeech(data)
	EndRecord()
	

all = [] 
p = pyaudio.PyAudio()

stream = p.open(format = FORMAT,
	channels = CHANNELS,
	rate = RATE,
	input = True,
	output = True,
	frames_per_buffer = chunk)

rmOldFiles(TmpLocation)

print "waiting for Speech"

while silence:

	try:

		input = GetStream(chunk)

	except:

		continue
	
	Frequency=Pitch(input);
	rms_value = rms(input)
		
	if (rms_value > Threshold) and (Frequency > VocalRange):
		#print "%f Frequency" %Frequency
		#print "%f Energy" %rms_value
		silence=False
		LastBlock=input
		print "Recording...."
	Time = Time + 1
	if (Time > TimeoutSignal):
		print "Time Out No Speech Detected"
		sys.exit()

RecordSpeech(TimeoutSignal, LastBlock)	
