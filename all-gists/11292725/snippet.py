#!/usr/bin/python

import os, time, signal, sys
from Adafruit_ADS1x15 import ADS1x15
import RPi.GPIO as GPIO
from datetime import datetime
import subprocess
import argparse
import requests
import json
import plotly

# look at your Plot.ly account
stream_tokens = ['aaaaaaaaaa', 'bbbbbbbbbb', 'ccccccccc', 'ddddddddd']

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.IN)

def signal_handler(signal, frame):
        #print 'You pressed Ctrl+C!'
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

#print 'Press Ctrl+C to exit'

ADS1015 = 0x00  # 12-bit ADC
ADS1115 = 0x01  # 16-bit ADC

# Initialise the ADC using the default mode (use default I2C address)
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
adc = ADS1x15(ic=ADS1115)

def logfunc( filename ):

    # Now do a differential reading of channels 2 and 3
    voltsdiff01 = adc.readADCDifferential01(4096, 250)/1000.0
    voltsdiff23 = adc.readADCDifferential23(4096, 250)/1000.0

    p = subprocess.Popen('sudo /home/pi/bin/LuxMeter'.split(), stdout=subprocess.PIPE)
    out, _ = p.communicate()
    lux = int( out.split(',')[3].split(':')[1] )

    row = "%s,%.4f,%.4f,%i,%i\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), -voltsdiff01, -voltsdiff23, GPIO.input(24), lux)

    with open( filename , "a") as f:
        f.write( row )

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S"), -voltsdiff01, -voltsdiff23, GPIO.input(24), lux

def streamdata():

    s0 = plotly.stream(stream_tokens[0])
    s1 = plotly.stream(stream_tokens[1])
    s2 = plotly.stream(stream_tokens[2])

    while True:
        moment, vin, vstor, batok, lux = logfunc( os.path.join(logfolder, filename) )
        s0.write({'x': moment, 'y': vin})
        s1.write({'x': moment, 'y': vstor})
        s2.write({'x': moment, 'y': lux})
        time.sleep(0.5)
    s0.close()
    s1.close()
    s2.close()

if __name__ == "__main__":

    filename = None
    logfolder = '/home/pi/smartlogs/'

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', default=None)
    args = parser.parse_args()

    if args.file is None:
        filename = '%s_luxvstor.log' % datetime.now().strftime("%Y%m%d")
    else:
        filename = args.file

    print "Log location: %s" % os.path.join(logfolder, filename)

    streamdata()