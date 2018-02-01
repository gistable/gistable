import threading                                                             
import time                                                                  
import sys                                                                   
import shared                                                                
                                                                             
shared.counter = 0                                                           
event = threading.Event()                                                    
                                                                             
def main():                                                                  
    import shared                                                            
    while True:                                                              
        shared.counter += 1                                                  
        time.sleep(1)                                                        
        if shared.counter % 2 == 0:                                          
            event.set()                                                      
        if shared.counter == 10:                                             
            sys.exit(1)                                                      
                                                                             
def secondary():                                                             
    import shared                                                            
                                                                             
    while True:                                                              
        print "event wait"                                                   
        sys.stdout.flush()                                                   
        event.wait()                                                         
        print "event arrived", shared.counter                                
        event.clear()                                                        
        if shared.counter == 10:                                             
            sys.exit(1)                                                      
                                                                             
thr1 = threading.Thread(target=main)                                         
thr1.start()                                                                 
                                                                             
thr2 = threading.Thread(target=secondary)                                    
thr2.start()                                                                 
                                                                             
thr1.join()  