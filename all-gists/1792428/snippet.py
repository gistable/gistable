# This is a monkeyrunner jython script that opens a connection to an Android
# device and starts camera app and makes photos by touching the camerabutton.
#
# See http://developer.android.com/guide/developing/tools/monkeyrunner_concepts.html
#
# usage: monkeyrunner photo_monkey.py
#

# Imports the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

# Connects to the current device
device = MonkeyRunner.waitForConnection()

# sets a variable with the package's internal name
package = 'com.android.camera'

# sets a variable with the name of an Activity in the package
activity = 'com.android.camera.Camera'

# sets the name of the component to start
runComponent = package + '/' + activity

# Runs the component
device.startActivity(component=runComponent)

# Position of the button
#x = 62
#y = 721

x = 722
y = 414

pause = 5


for i in range(1, 4):
    # Every so often inject a touch to spice things up!
    device.touch(x, y, 'DOWN_AND_UP')
    MonkeyRunner.sleep(pause)
    