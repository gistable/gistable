from datetime import datetime, timedelta
import functools


def timed_cache(**timedelta_kwargs):                                              
                                                                                  
    def _wrapper(f):                                                              
        update_delta = timedelta(**timedelta_kwargs)                              
        next_update = datetime.utcnow() - update_delta                            
        # Apply @lru_cache to f with no cache size limit                          
        f = functools.lru_cache(None)(f)                                          
                                                                                                                      
        @functools.wraps(f)                                                       
        def _wrapped(*args, **kwargs):                                            
            nonlocal next_update                                                  
            now = datetime.utcnow()                                               
            if now >= next_update:                                                
                f.cache_clear()                                                   
                next_update = now + update_delta                                
            return f(*args, **kwargs)                                             
        return _wrapped                                                           
    return _wrapper