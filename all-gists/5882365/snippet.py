from array import array
import pyaudio
import sys
import numpy as np
import matplotlib.pyplot as plt

plt.ion()
ax1=plt.axes()  
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
#RATE = 44100
RATE = 16000
RECORD_SECONDS = 20

p = pyaudio.PyAudio()
signal = np.zeros([1,1024])[0]
ii16 = np.iinfo(np.int16)
plt.ylim([ii16.min,ii16.max])
plt.grid()
line, = plt.plot(signal)

stream = p.open(format = FORMAT,
                channels = CHANNELS, 
                rate = RATE, 
                input = True,
                output = True,
                frames_per_buffer = chunk)

for i in range(0, 44100 / chunk * RECORD_SECONDS):
    data = stream.read(chunk)
    signal = np.fromstring(data, 'Int16')
    line.set_xdata(np.arange(len(signal)))
    line.set_ydata(signal)
    plt.draw()

stream.stop_stream()
stream.close()
p.terminate()
