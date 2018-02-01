#!/usr/bin/env python3

# Adapted from http://www.creativetux.com/2012/11/streaming-to-twitchtv-with-linux.html
#
# Make sure to put your twitch.tv key in a file called "key" in the current directory.
#
# Before running, make sure PulseAudio is set up with the correct loopback modules
# and a null sink named "mix". You can use something ilke the following commands:
#
# pactl load-module module-null-sink sink_name=mix
# pactl load-module module-loopback sink=mix
# pactl load-module module-loopback sink=mix
#
# Then go in with the `pavucontrol` utility and set the inputs for both loopbacks:
# one as a monitor of your audio out, and one for your microphone in. Do this on the
# recording tab (you may have to select "show All Streams")
#
# NOTE: for non-debian distros, change "avconv" to "ffmpeg" below, and any other
# necessary changes to the command arguments.

import subprocess

output = subprocess.check_output("xwininfo", universal_newlines=True)

properties = {}
for line in output.split("\n"):
    if ":" in line:
        parts = line.split(":",1)
        properties[parts[0].strip()] = parts[1].strip()

TOPXY="{},{}".format(properties["Absolute upper-left X"],
                     properties["Absolute upper-left Y"])
INRES="{}x{}".format(properties["Width"],
                     properties["Height"])
OUTRES=INRES
FPS="30"
QUAL="medium"
STREAM_KEY=open("key","r").read().strip()

subprocess.call(["avconv",
    "-f", "x11grab", "-s", INRES, "-r", FPS, "-i", ":0.0+{}".format(TOPXY),
    "-v", "verbose",
#    "-f", "video4linux2", "-s", INRES, "-r", FPS, "-i", "/dev/video1",
    "-f", "pulse", "-i", "mix.monitor",
    "-vcodec", "libx264", "-s", OUTRES, "-pre:v", QUAL,
    "-acodec", "libmp3lame", "-ar", "44100", "-threads", "auto", "-qscale", "3", "-b", "712000", "-bufsize", "512k",
    "-f", "flv", "rtmp://live.justin.tv/app/{}".format(STREAM_KEY)
    ])
