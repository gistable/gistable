from socketserver import TCPServer, StreamRequestHandler, ThreadingMixIn
import threading

class TCPThreadedServer(TCPServer, ThreadingMixIn):
    class RequestHandler(StreamRequestHandler):
       def handle(self):
           msg = self.rfile.readline().decode('utf-8').strip()
           reply = self.server.process(msg)
           if reply is not None:
               self.wfile.write((reply + '\n').encode('utf-8'))

    def __init__(self, host, port, name=None):
        self.allow_reuse_address = True
        TCPServer.__init__(self, (host, port), self.RequestHandler)
        if name is None: name = "%s:%s" % (host, port)
        self.name = name
        self.poll_interval = 0.5

    def process(self, msg):
        """
        should be overridden
        process a message
        msg    - string containing a received message
        return - if returns a not None object, it will be sent back 
                 to the client.
        """
        raise NotImplemented

    def serve_forever(self, poll_interval=0.5):
        self.poll_interval = poll_interval
        self.trd = threading.Thread(target=TCPServer.serve_forever,
                                    args = [self, self.poll_interval],
                                    name = "PyServer-" + self.name)
        self.trd.start()

    def shutdown(self):
        TCPServer.shutdown(self)
        TCPServer.server_close(self)
        self.trd.join()
        del self.trd

if __name__ == "__main__":

    import socket
    def client(ip, port, msg, recv_len=4096, 
               timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        msg = str(msg)
        response = None
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((ip, port))
            if timeout != socket._GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            sock.send((msg + "\n").encode('utf-8'))
            if recv_len > 0:
                response = sock.recv(recv_len).decode('utf-8')
        finally:
            sock.close()
            return response
    
    class EchoServerExample(TCPThreadedServer):
        def __init__(self):
            TCPThreadedServer.__init__(self, "localhost", 1234, "Server")
    
        def process(self, data):
            print("EchoServer Got: " + data)
            return str.upper(data)
    
    for i in range(10):
        echo = EchoServerExample()
        echo.serve_forever()
    
        response = client("localhost", 1234, "hi-%i" % i)
        print("Client received: " + response)
    
        echo.shutdown()
    
