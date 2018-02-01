   #
   # I inherited a large code base, where hundreds of code paths end up
   # calling "common_function_called_in_gazillion_places". 
   #
   # And the need arose for this function to access the HTTP request's
   # headers... 
   #
   # What to do? Refactor all the places leading up to here? In a dynamically
   # typed language, with no compiler to tell us the places to refactor?
   #
   # NO - let's hack the universe instead.
   
   def get_the_request():
      """
      Look up the call stack to see if one of our callers has "self.request"
      (i.e. the Pyramid request) and if so, return it
      """
       for f in inspect.stack():
           if 'self' in f[0].f_locals:
               self = f[0].f_locals['self']
               if hasattr(self, 'request'):
                   return self.request
       else:
           return None

   def common_function_called_in_gazillion_places( variables, action ):
       ...      
       # Get the request from our callers, and extract the IP from it
       request = get_the_request()
       if request is not None:
           ip_addr = request.remote_addr
           if 'X-Forwarded-For' in request.headers:
               ip_addr = request.headers['X-Forwarded-For']
           if ip_addr not in ['127.0.0.1', 'localhost'] and \
                   isinstance(ip_addr, (str,unicode)):
               event_data['context'] = {'ip': ip_addr}
            ....
   # TADA!!!
   #
   # OK, now I can burn in programmer Hell - for all eternity.