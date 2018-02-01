# import libraries
import time 
import os 

while True: # do forever

    

    os.system('fswebcam -r 320x240 -S 3 --jpeg 50 --save /home/pi/to_transmit/%H%M%S.jpg') # uses Fswebcam to take picture

    time.sleep(15) # this line creates a 15 second delay before repeating the loop

