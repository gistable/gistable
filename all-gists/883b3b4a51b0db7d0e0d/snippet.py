#!/usr/bin/env python                                           
                                                                
import apscheduler.scheduler                                    
import daemon.runner                                            
import os.path                                                  
import sys                                                      
import time                                                     
                                                                
class Core():                                                   
    def __init__(self):                                         
        """Daemon behaviour"""                                  
        self.stdin_path      = '/dev/null'                      
        self.stdout_path     = '/dev/tty'                       
        self.stderr_path     = '/dev/tty'                       
        self.pidfile_path    = os.path.realpath('core.pid')     
        self.pidfile_timeout = 5                                
        self.sched           = apscheduler.scheduler.Scheduler()
        self.sched.standalone = True                            
                                                                
    def run(self):                                              
        """Main daemon loop"""                                  
        try:                                                                                                     
            @self.sched.interval_schedule(seconds=5)            
            def running():                                      
                print "Running..."
                
            self.sched.start()  
                                                                
        except:                                                 
            self.sched.shutdown()                               
            print "Unexpected error:", sys.exc_info()           
            sys.exit(1)                                         
                                                                
if __name__ == "__main__":                                      
    if len(sys.argv) == 2:                                      
        core   = Core()                                         
        runner = daemon.runner.DaemonRunner(core)               
                                                                
        runner.do_action() # start|stop|restart as sys.argv[1]  
    else:                                                       
        print "Usage: %s start|stop|restart" % sys.argv[0]      
        sys.exit(1)                                             
else:                                                           
    print "Core daemon can't be included in another program."   
    sys.exit(1)