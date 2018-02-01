#!/usr/bin/env python
#To run this script in terminal first to install this dependancy: sudo apt-get install xdotool
#To make it excutable GoTo the file directory and run the command: chmod u+x upwork_tracker_free_time.rb
#Now you just need to run this file using form termial :~ ./upwork_tracker_free_time.rb
#Note: You need to specifiy every on which work space you want to swicth tab currently In code I am only swithching termial 
#But you can also switch browser tab or sublim tabs subprocess.call("xdotool key ctrl+Tab" ,shell=True)
#Enjoy :)
import subprocess
import time
subprocess.call("xdotool key ctrl+alt+Up" ,shell=True)
time.sleep(60)
subprocess.call("xdotool key ctrl+alt+Left" ,shell=True)
time.sleep(60)
subprocess.call("xdotool key ctrl+alt+Right" ,shell=True)
time.sleep(60)
subprocess.call("xdotool key ctrl+alt+Left" ,shell=True)
time.sleep(60)
subprocess.call("xdotool key ctrl+alt+Right" ,shell=True)

time.sleep(60)
subprocess.call("xdotool key ctrl+alt+Left" ,shell=True)
time.sleep(60)
subprocess.call("xdotool key ctrl+alt+Right" ,shell=True)

subprocess.call("xdotool key ctrl+alt+Left" ,shell=True)

