import signal

class GracefulInterruptHandler(object):
    
    def __init__(self, sig=signal.SIGINT):
        self.sig = sig
        
    def __enter__(self):
        
        self.interrupted = False
        self.released = False
        
        self.original_handler = signal.getsignal(self.sig)
        
        def handler(signum, frame):
            self.release()
            self.interrupted = True
            
        signal.signal(self.sig, handler)
        
        return self
        
    def __exit__(self, type, value, tb):
        self.release()
        
    def release(self):
        
        if self.released:
            return False

        signal.signal(self.sig, self.original_handler)
        
        self.released = True
        
        return True
        

if __name__ == '__main__':

    import unittest
    import time
                
    class GracefulInterruptHandlerTestCase(unittest.TestCase):
        
        def test_simple(self):
            with GracefulInterruptHandler() as h:
                while True:
                    print "..."
                    time.sleep(1)
                    if h.interrupted:
                        print "interrupted!"
                        time.sleep(5)
                        break
                    
        def test_nested(self):
            with GracefulInterruptHandler() as h1:
                while True:
                    print "(1)..."
                    time.sleep(1)
                    with GracefulInterruptHandler() as h2:
                        while True:
                            print "\t(2)..."
                            time.sleep(1)
                            if h2.interrupted:
                                print "\t(2) interrupted!"
                                time.sleep(2)
                                break
                    if h1.interrupted:
                        print "(1) interrupted!"
                        time.sleep(2)
                        break
                        
    unittest.main()
