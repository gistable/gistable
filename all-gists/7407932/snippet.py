#!/usr/bin/python

#
# A simple Motion JPEG server in python for creating "virtual cameras" from video sequences.
# 
# The cameras will support MJPEG streaming over HTTP. The MJPEG streams are formed from static JPEG images.
# If you wish to stream a video file, use a tool like VirtualDub to break the video into a sequence of JPEGs.
# 
# The list of cameras should be defined as a series of entries in a file named 'mjpeg-server.conf', with
# each entry having the following format:
# 
# [Camera-1]
# images: /tmp/video-1/frames
# port: 8001
# maxfps: 10
# 
# The above entry creates a virtual camera named "Camera-1" on local port 8001. The .jpg files found in the
# "/tmp/video-1/frames" directory will be served as an MJPEG stream with a max speed of 10 fps. You can access
# this stream from any MJPEG client (such as your browser) at: http://<server ip>:8001
# 
# Copyright (c) 2013 Arun Nair (http://nairteashop.org).
# Licensed under the MIT license.
#

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from threading import Thread
import ConfigParser
import logging
import time
import os

SERVERS = {}

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Get client info
        client = self.client_address

        # Get the port the client connected to
        port = self.server.server_port

        # Get the image files corresponding to this port
        imageDir = SERVERS[port]["images"]
        imageFiles = os.listdir( imageDir )
        imageFiles.sort()

        # Get the min intra frame delay
        maxFPS = SERVERS[port]["maxfps"]
        if maxFPS == 0:
            minDelay = 0
        else:
            minDelay = 1.0 / maxFPS

        logging.info( "Serving client %s:%s from port %s at %s fps", client[0], client[1], port, maxFPS )

        # Send headers
        self.send_response( 200 )
        self.send_header( "Cache-Control", "no-cache" )
        self.send_header( "Pragma", "no-cache" )
        self.send_header( "Connection", "close" )
        self.send_header( "Content-Type", "multipart/x-mixed-replace; boundary=--myboundary" )
        self.end_headers()

        o = self.wfile

        # Send image files in a loop
        lastFrameTime = 0
        while True:
            for imageFile in imageFiles:
                f = open( os.path.join(imageDir, imageFile) )
                contents = f.read()
                f.close()

                # Wait if required so we stay under the max FPS
                if lastFrameTime != 0:
                    now = time.time()
                    delay = now - lastFrameTime
                    if delay < minDelay:
                        logging.debug( "Waiting for ", (minDelay - delay) )
                        time.sleep( minDelay - delay )

                try:
                    logging.debug( "Serving frame %s", imageFile )
                    o.write( "--myboundary\r\n" )
                    o.write( "Content-Type: image/jpeg\r\n" )
                    o.write( "Content-Length: %s\r\n" % len(contents) )
                    o.write( "\r\n" )
                    o.write( contents )
                    o.write( "\r\n" )
                except:
                    logging.info( "Done serving client %s:%s from port %s", client[0], client[1], port )
                    return

                lastFrameTime = time.time()

            logging.info( "Re-looping for client %s:%s from port %s", client[0], client[1], port )

class ThreadingHTTPServer( ThreadingMixIn, HTTPServer ):
    pass

def startServer( port ):
    def target( port ):
        server = ThreadingHTTPServer( ("0.0.0.0",port), RequestHandler )
        server.serve_forever()

    t = Thread( target=target, args=[port] )
    t.start()

if __name__ == "__main__":
    logging.basicConfig( level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s" )

    config = ConfigParser.ConfigParser()
    config.read( "mjpeg-server.conf" )

    for section in config.sections():
        images = config.get( section, "images" )
        port   = config.getint( section, "port" )
        maxfps = config.getint( section, "maxfps" )

        SERVERS[port] = { "images": images, "maxfps": maxfps }
        startServer( port )
        logging.info( "Serving '%s' on port %s" % (section, port) )
