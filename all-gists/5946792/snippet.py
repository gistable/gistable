#!/usr/bin/env python
from datetime import datetime, timedelta
import time
import sys
import os

if len(sys.argv) is 3:
    music_service = str(sys.argv[1])
    minutes_to_wait = float(sys.argv[2])
else:
    print "Usage:", sys.argv[0], "[itunes or spotify] [minutes to wait (fractions are allowed)]"
    minutes_to_wait = False

start = datetime.now()
if minutes_to_wait:
    # Calculate when we should be done, for display purposes
    finish = start + timedelta(minutes=minutes_to_wait)

    # Wait the proper amount of time, while printing a timer
    print "Turning off music in:"
    for i in xrange(1, int(minutes_to_wait * 60)):
        time.sleep(1)
        newtime = datetime.now()
        time_left = str(finish - newtime)

        sys.stdout.write("\r" + time_left)
        sys.stdout.flush()

    if music_service == "spotify":
        # Pause spotify when this is over using osx's applescript
        os.system("osascript -e 'tell app \"spotify\" to playpause'")
    if music_service == "itunes":
        # Pause itunes when this is over using osx's applescript
        os.system("osascript -e 'tell app \"itunes\" to playpause'")
