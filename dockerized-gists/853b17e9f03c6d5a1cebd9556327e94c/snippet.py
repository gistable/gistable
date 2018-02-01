import SimpleHTTPServer
import SocketServer

# Redirect to Google.com
class Redirect(SimpleHTTPServer.SimpleHTTPRequestHandler):
   def do_GET(self):
       print self.path
       self.send_response(301)
       new_path = '%s%s'%('https://google.com', self.path)
       self.send_header('Location', new_path)
       self.end_headers()

# Listen on 127.0.0.1:8000
SocketServer.TCPServer(("127.0.0.1", 8000), Redirect).serve_forever()