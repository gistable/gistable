#!/usr/bin/env python

"""
Requires pychromecast.

Install with `pip install pychromecast`

usage: cast.py [-h] -d DEVICE -v VIDEO

Cast YouTube videos headlessly.

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        Name of device to cast to. Choose: Living Room
  -v VIDEO, --video VIDEO
                        YouTube video ID (part after ?v= in the URL)
"""
import time
import signal
import argparse
from threading import Event

import pychromecast
from pychromecast.controllers.youtube import YouTubeController

# Triggers program exit
shutdown = Event()

def signal_handler(x,y):
   shutdown.set()

# Listen for these signals
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# A list of Chromecast devices broadcasting
chromecast_devices = ', '.join(pychromecast.get_chromecasts_as_dict().keys())

# Some command line help
parser = argparse.ArgumentParser(description='Cast YouTube videos headlessly.')
parser.add_argument('-d', '--device', required=True, help='Name of device to cast to. Choose: %s' % chromecast_devices)
parser.add_argument('-v', '--video', required=True, help='YouTube video ID (part after ?v= in the URL)')

opts = parser.parse_args()

cast_device = opts.device
youtube_id = opts.video

# Initialize a connection to the Chromecast
cast = pychromecast.get_chromecast(friendly_name=cast_device)

# Create and register a YouTube controller
yt = YouTubeController()
cast.register_handler(yt)

# Play the video ID we've been given
yt.play_video(youtube_id)

print("Streaming %s to %s" % (youtube_id, cast_device))

# Wait for a signal that we should shut down
while not shutdown.is_set():
   time.sleep(1)

print("Stopping stream...")
cast.quit_app()