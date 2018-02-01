# how to run: monkerunner snapshot.py [filename]
import datetime, sys
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

if len(sys.argv) > 1:
    filename = sys.argv[1]
    if not filename.endswith(".png"):
        filename = "%s.png" % filename
else:
    now = datetime.datetime.now()
    filename = now.strftime("device-%Y-%m-%d-%H%M%S.png")

print "Taking snapshot: %s" % filename
  
device = MonkeyRunner.waitForConnection()
result = device.takeSnapshot()
result.writeToFile(filename,'png')
