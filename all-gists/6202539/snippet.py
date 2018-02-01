#!/usr/bin/env monkeyrunner                                                         
                                                                                    
import time                                                                         
                                                                                    
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice                     
                                                                                    
device = MonkeyRunner.waitForConnection()                                           
     
# Touch down screen                                                                               
device.touch(100, 500, MonkeyDevice.DOWN)                                           

# Move from 100, 500 to 300, 500
for i in range(1, 11):                                                              
    device.touch(100 + 20 * i, 500, MonkeyDevice.MOVE)                              
    print "move ", 100 + 20 * i, 500                                                
    time.sleep(0.1)             

# Move from (300, 500 to 200, 500)                                                    
for i in range(1, 11):                                                              
    device.touch(300, 500 - 10 * i, MonkeyDevice.MOVE)                              
    print "move ", 300, 500 - 10 * i                                                
    time.sleep(0.1)                                                                 

# Remove finger from screen
device.touch(300, 400, MonkeyDevice.UP) 