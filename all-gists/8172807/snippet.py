import logging
from mpi4py import MPI

class MPIFileHandler(logging.FileHandler):                                      
    def __init__(self,filename, mode=MPI.MODE_WRONLY|MPI.MODE_CREATE|MPI.MODE_APPEND , encoding=None, delay=0, comm=MPI.COMM_WORLD ):
        encoding = None                                                         
        self.baseFilename = os.path.abspath(filename)                           
        self.mode = mode                                                        
        self.encoding = encoding                                                
        self.comm = comm                                                        
        if delay:                                                               
            #We don't open the stream, but we still need to call the            
            #Handler constructor to set level, formatter, lock etc.             
            logging.Handler.__init__(self)                                      
            self.stream = None                                                  
        else:                                                                   
           logging.StreamHandler.__init__(self, self._open())                   
                                                                                
    def _open(self):                                                            
        stream = MPILogFile.Open( self.comm, self.baseFilename, self.mode )     
        stream.Set_atomicity(True)                                              
        return stream                                                           
                                                                                
    def close(self):                                                            
        if self.stream:                                                         
            self.stream.Sync()                                                  
            self.stream.Close()                                                 
            self.stream = None                                                  
  
if __name__ == "__main__":
    comm = MPI.COMM_WORLD                                                           
    logger = logging.getLogger("node[%i]"%comm.rank)                                
    logger.setLevel(logging.DEBUG)                                                  
                                                                                    
    mh = MPIFileHandler("test.log")                                           
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    mh.setFormatter(formatter)                                                      
                                                                                    
    logger.addHandler(mh)                                                           
    # 'application' code                                                            
    logger.debug('debug message')                                                   
    logger.info('info message')                                                     
    logger.warn('warn message')                                                     
    logger.error('error message')                                                   
    logger.critical('critical message')    