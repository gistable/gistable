# A simple limiter

from sounddevice import Stream, CallbackStop
from time import sleep
from numpy import array, random, zeros
import matplotlib.pyplot as plt

################################### Constants ##################################

fs            = 44100   # Hz
threshold     = 0.6     # absolute gain
delay         = 40      # samples
signal_length = 1       # second
release_coeff = 0.9995  # release time factor
attack_coeff  = 0.9     # attack time factor
block_length  = 1024    # samples

#################### Generate quiet-loud-quiet noise signal ####################

signal = array(random.rand(fs*signal_length)*2-1)
signal[:signal_length*fs/3] *= 0.1
signal[signal_length*fs*2/3:] *= 0.1

############################# Implementation of Limiter ########################

class Limiter:
    def __init__(self, attack_coeff, release_coeff, delay, threshold):
        self.delay_index = 0
        self.envelope = 0
        self.gain = 1
        self.delay = delay
        self.delay_line = zeros(delay)
        self.release_coeff = release_coeff
        self.attack_coeff = attack_coeff
        self.threshold = threshold

    def limit(self, signal):
        for idx, sample in enumerate(signal):
            self.delay_line[self.delay_index] = sample
            self.delay_index = (self.delay_index + 1) % self.delay

            # calculate an envelope of the signal
            self.envelope  = max(abs(sample), self.envelope*self.release_coeff)

            if self.envelope > self.threshold:
                target_gain = self.threshold / self.envelope
            else:
                target_gain = 1.0

            # have self.gain go towards a desired limiter gain
            self.gain = ( self.gain*self.attack_coeff +
                          target_gain*(1-self.attack_coeff) )

            # limit the delayed signal
            signal[idx] = self.delay_line[self.delay_index] * self.gain
        return signal

################################# Play the Audio ###############################

original_signal = array(signal, copy=True)
output_signal = array(signal, copy=True)

limiter = Limiter(attack_coeff, release_coeff, delay, threshold)

def callback(indata, outdata, frames, time, status):
    if status:
        print("Playback Error: {}".format(status))
    played_frames = callback.counter
    callback.counter += frames
    if callback.counter > len(signal):
        raise CallbackStop()
    limited_signal = limiter.limit(signal[played_frames:callback.counter])
    outdata[:, 0] = limited_signal
    output_signal[played_frames:callback.counter] = limited_signal

callback.counter = 0

with Stream(channels=1, callback=callback) as s:
    while s.active:
        sleep(0.1)

############################## Plot results ####################################

plt.figure()
plt.plot(original_signal, color='grey', label='original signal')
plt.plot(output_signal, color='black', label='limited signal')
plt.legend()
plt.show(block=True)
