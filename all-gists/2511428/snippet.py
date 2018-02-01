# adjusted for a Samsung Galaxy Nexus running ICS, Soundhound and Skype installed, not really reusable.

# Imports the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

# # Connects to the current device, returning a MonkeyDevice object
device = MonkeyRunner.waitForConnection()

# sets a variable with the package's internal name
package = 'com.melodis.midomiMusicIdentifier'

# sets a variable with the name of an Activity in the package
activity = 'com.soundhound.android.appcommon.activity.SoundHound'

# sets the name of the component to start
runComponent = package + '/' + activity

# Runs the component
device.startActivity(component=runComponent)

# wait
MonkeyRunner.sleep(2)

# listen to a new song
device.touch(350, 340, MonkeyDevice.DOWN_AND_UP)

MonkeyRunner.sleep(25)

# Takes a screenshot
result = device.takeSnapshot()

# Writes the screenshot to a file
result.writeToFile('screenshot.png', 'png')

# share the song
device.touch(480, 100, MonkeyDevice.DOWN_AND_UP)

# wait
MonkeyRunner.sleep(5)

# more share options
device.touch(570, 100, MonkeyDevice.DOWN_AND_UP)
# wait
MonkeyRunner.sleep(4)

# EMAIL
# select email from the list
device.touch(360, 580, MonkeyDevice.DOWN_AND_UP)
# wait
MonkeyRunner.sleep(2)
# type email address - DISABLED
# device.type('luis@ribot.co.uk')
# # send
# device.touch(570, 100, MonkeyDevice.DOWN_AND_UP)

# copy message body
# * copy paste *
# select word
device.drag((340, 600), (340, 600), 2, 1)
# wait
MonkeyRunner.sleep(1)
# select all
device.touch(340, 100, MonkeyDevice.DOWN_AND_UP)
# wait
MonkeyRunner.sleep(1)
# cut
device.touch(430, 100, MonkeyDevice.DOWN_AND_UP)
# wait
MonkeyRunner.sleep(1)

# PASTE TO SKYPE
# switch to skype
device.startActivity(component='com.skype.raider/com.skype.raider.Main')
# wait
MonkeyRunner.sleep(2)
# go home
device.touch(60, 100, MonkeyDevice.DOWN_AND_UP)
# wait
MonkeyRunner.sleep(2)
# press recent
device.touch(520, 460, MonkeyDevice.DOWN_AND_UP)
# wait
MonkeyRunner.sleep(2)
# press item on top of the list
device.touch(350, 280, MonkeyDevice.DOWN_AND_UP)
# wait
MonkeyRunner.sleep(2)
# press the input field
device.touch(350, 1135, MonkeyDevice.DOWN_AND_UP)
# wait
MonkeyRunner.sleep(2)
# paste
device.drag((60, 608), (60, 608), 3, 1)
device.touch(60, 530, MonkeyDevice.DOWN_AND_UP)
# press return
device.press('KEYCODE_ENTER', MonkeyDevice.DOWN_AND_UP)