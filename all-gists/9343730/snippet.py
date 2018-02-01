#!/usr/bin/python
'''
  A Simple mjpg stream http server for the Raspberry Pi Camera
  inspired by https://gist.github.com/n3wtron/4624820
'''
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import io
import time
import picamera

camera=None
 

class CamHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path.endswith('.mjpg'):
      self.send_response(200)
      self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
      self.end_headers()
      stream=io.BytesIO()
      try:
        start=time.time()
        for foo in camera.capture_continuous(stream,'jpeg'):
          self.wfile.write("--jpgboundary")
          self.send_header('Content-type','image/jpeg')
          self.send_header('Content-length',len(stream.getvalue()))
          self.end_headers()
          self.wfile.write(stream.getvalue())
          stream.seek(0)
          stream.truncate()
          time.sleep(.5)
      except KeyboardInterrupt:
        pass 
      return
    else:
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write("""<html><head></head><body>
        <img src="/cam.mjpg"/>
      </body></html>""")
      return

def main():
  global camera
  camera = picamera.PiCamera()
  #camera.resolution = (1280, 960)
  camera.resolution = (640, 480)
  global img
  try:
    server = HTTPServer(('',8080),CamHandler)
    print "server started"
    server.serve_forever()
  except KeyboardInterrupt:
    camera.close()
    server.socket.close()

if __name__ == '__main__':
  main()
