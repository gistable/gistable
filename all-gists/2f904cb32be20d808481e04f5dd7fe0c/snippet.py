from microbit import *

analog_0 = 0
counter = 0
previous_running_time = 0    
target = 20000              
pulse = 0                    
remind = 0                  

while True:
    
    current_running_time = running_time()
    analog_0 = pin0.read_analog()
    
    
    if (remind == 0):
        if (analog_0 >= 920):
            display.show(Image.HEART)
            counter = counter + 1
            remind = 1
    
    if (remind == 1):
        if (analog_0 < 920):
            display.clear()
            remind = 0
    
    if ((current_running_time - previous_running_time) >= target):
        
        counter = counter * 3
        display.scroll("%d bpm" % (counter), delay=100,)
                
        counter = 0
        previous_running_time = running_time()