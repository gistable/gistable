class StreamHandler(tornado.web.RequestHandler): 
    @tornado.web.asynchronous 
    def get(self):
        self.post()
        
    @tornado.web.asynchronous 
    def post(self):
        self.ioloop = tornado.ioloop.IOLoop.instance() 
        self.pipe = self.get_pipe()
        self.ioloop.add_handler( 
            self.pipe.fileno(), 
            self.async_callback (self.on_read), 
            self.ioloop.READ)
        
        # optional: close pipe after 20 seconds
        self.ioloop.add_timeout(time.time()+(20), self.close_pipe)
        
    def close_pipe(self):
        self.ioloop.remove_handler(self.pipe)
        # add link to end user to load more output
        self.write('''
            <script>
                (function(){
                    document.write("</pre>");
                    document.write("<a href='javascript:location.href=location.href'>load more...</a>");
                    document.body.scrollTop = document.body.scrollHeight;
                })()
            </script>        
        ''')
        self.finish()
        self.pipe.close()
        
        try:
            self.process.kill()
        except:
            pass
        
    def on_read(self, fd, events): 
        buffer = self.pipe.read(256) 
        try: 
            assert buffer 
            self.write(buffer) 
            self.flush() 
        except: 
            self.close_pipe()
            
    def _spawn_process(self, commandline):
        self.process = subprocess.Popen(
            commandline, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stdin=subprocess.PIPE, 
            stderr=subprocess.PIPE)
            
        return self.process
        
    def _get_pipe(self, commandline):
        return self._spawn_process(commandline).stdout
            
    def get_pipe(self):
        # /dev/urandom example, tail- f /var/log/syslog can work fine as well
        return self._get_pipe('cat /dev/urandom')
