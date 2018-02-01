#!/usr/bin/env python

import threading
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

# GPIO pins

# gpio readall
# ...
#[pi wedge]                   [physical GPIO.BOARD]
# |  17 |   0 | GPIO. 0 |   IN | 0 | 11 || 12 | 0 | IN   | GPIO. 1 | 1   | 18  |
# |  27 |   2 | GPIO. 2 |   IN | 0 | 13 || 14 |   |      | 0v      |     |     |
# |  22 |   3 | GPIO. 3 |   IN | 0 | 15 || 16 | 0 | IN   | GPIO. 4 | 4   | 23  |
# ...

BUTTON_VOLUME_UP = 11
BUTTON_VOLUME_DOWN = 12
BUTTON_CHANNEL_UP = 13
BUTTON_CHANNEL_DOWN = 15

GPIO.setup([BUTTON_VOLUME_UP, BUTTON_VOLUME_DOWN, BUTTON_CHANNEL_UP, BUTTON_CHANNEL_DOWN],
    # enable internal pull-down resistors to default the inputs low
    # see https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
    GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Sun Jun  5 09:59:50 2016
##################################################

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser
import osmosdr

class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6
        self.channel_width = channel_width = 200e3
        self.channel_freq = channel_freq = 97.7e6
        self.center_freq = center_freq = 97.9e6
        self.audio_gain = audio_gain = 1.5

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=12,
                decimation=5,
                taps=None,
                fractional_bw=None,
        )
        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(97.9e6, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(0, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna("", 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
          
        self.low_pass_filter_0 = filter.fir_filter_ccf(int(samp_rate/channel_width), firdes.low_pass(
        	1, samp_rate, 75e3, 25e3, firdes.WIN_BLACKMAN, 6.76))
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((audio_gain, ))
        self.audio_sink_0 = audio.sink(48000, "hw:0,1", True)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=480e3,
        	audio_decimation=10,
        )
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, center_freq - channel_freq, 1, 0)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.analog_wfm_rcv_0, 0), (self.blocks_multiply_const_vxx_0, 0))



    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 75e3, 25e3, firdes.WIN_BLACKMAN, 6.76))

    def get_channel_width(self):
        return self.channel_width

    def set_channel_width(self, channel_width):
        self.channel_width = channel_width

    def get_channel_freq(self):
        return self.channel_freq

    def set_channel_freq(self, channel_freq):
        self.channel_freq = channel_freq
        self.analog_sig_source_x_0.set_frequency(self.center_freq - self.channel_freq)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.analog_sig_source_x_0.set_frequency(self.center_freq - self.channel_freq)

    def get_audio_gain(self):
        return self.audio_gain

    def set_audio_gain(self, audio_gain):
        self.audio_gain = audio_gain
        self.blocks_multiply_const_vxx_0.set_k((self.audio_gain, ))

class ButtonThread(threading.Thread):
    def __init__(self, tb):
        self.tb = tb
        threading.Thread.__init__(self)

    def run(self):
        tb = self.tb

        while True:
            #print GPIO.input(BUTTON_VOLUME_UP), GPIO.input(BUTTON_VOLUME_DOWN), GPIO.input(BUTTON_CHANNEL_UP), GPIO.input(BUTTON_CHANNEL_DOWN)

            # Volume controls
            if GPIO.input(BUTTON_VOLUME_UP) == 1:
                tb.set_audio_gain(tb.get_audio_gain() + 1)
                print tb.get_audio_gain()
                # TODO: smaller steps when near zero?
                # TODO: don't let go below zero and wrap around

            if GPIO.input(BUTTON_VOLUME_DOWN) == 1:
                tb.set_audio_gain(tb.get_audio_gain() - 1)
                print tb.get_audio_gain()
                # TODO: limit to reasonable value that causes distortion

            # Channel controls
	    # TODO: ?
            if GPIO.input(BUTTON_CHANNEL_UP) == 1:
                # 0.4 MHz for expediency, most channels this far apart (though some 0.2)
                tb.set_channel_freq(tb.get_channel_freq() + 0.4e6)
                print tb.get_channel_freq()
            if GPIO.input(BUTTON_CHANNEL_DOWN) == 1:
                tb.set_channel_freq(tb.get_channel_freq() - 0.4e6)
                print tb.get_channel_freq()

            # TODO: edge-triggered?
            time.sleep(0.1)

if __name__ == '__main__':
    import ctypes
    import sys
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = top_block()
    ButtonThread(tb).start()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()
