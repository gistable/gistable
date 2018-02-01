import SimpleHTTPServer
import SocketServer

PORT = 8888

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
httpd = SocketServer.TCPServer(("", PORT), Handler)

print 'Serving at localhost:' + str(PORT)
httpd.serve_forever()