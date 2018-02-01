#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SYNOPSIS

    flask_gridfs_images.py --start
    flask_gridfs_images.py --add <IMAGE_URL>
    
DESCRIPTION

    Use the --add option to download and insert an image into a mongo gridfs
    collection. Use the --start option to start a Flask application that can
    serve images at the url /example_image.jpg.    
    
AUTHOR

    Jason Cupp <jason at cuppster.com>
    
LICENSE
    
    Public Domain

"""

from flask import Flask, send_file

import argparse
import cStringIO
import mimetypes
import requests
from PIL import Image

from pymongo import Connection
import gridfs


# setup mongo
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# connect to the database & get a gridfs handle
mongo_con = Connection(MONGODB_HOST, MONGODB_PORT)
grid_fs = gridfs.GridFS(mongo_con.test_database)


def serve_pil_image(pil_img):
    """
    see: 
        https://groups.google.com/forum/?fromgroups=#!topic/python-tornado/B19D6ll_uZE
        http://stackoverflow.com/questions/7877282/how-to-send-image-generated-by-pil-to-browser
    """
    img_io = cStringIO.StringIO() 
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')
    
    
def add_image(image_url):
    """add an image to mongo's gridfs"""
        
    # gridfs filename
    gridfs_filename = 'example_image.jpg'        
   
    # guess the mimetype and request the image resource
    mime_type = mimetypes.guess_type(image_url)[0]        
    r = requests.get(image_url, stream=True)
 
    # insert the resource into gridfs using the raw stream
    _id = grid_fs.put(r.raw, contentType=mime_type, filename=gridfs_filename)
    print "created new gridfs file {0} with id {1}".format(gridfs_filename, _id)


def start():
    """start the flask service"""
    
    # create app
    app = Flask(__name__)
    app.debug = True
    
    # our ONE route, to serve up image from gridfs
    @app.route('/image/<path:filename>')
    def get_image(filename):        
        """retrieve an image from mongodb gridfs"""
        
        if not grid_fs.exists(filename=filename):
            raise Exception("mongo file does not exist! {0}".format(filename))
        
        im_stream = grid_fs.get_last_version(filename)
        im = Image.open(im_stream)
        return serve_pil_image(im)
    
    
    # let's go!
    app.run()
    

def main():
    
    # CLI
    parser = argparse.ArgumentParser()    
    parser.add_argument('--start', action='store_true', help='start the service')
    parser.add_argument('--add', help='add an image via URL')    
    args = parser.parse_args()
    
    if args.start:
        start()
    elif args.add:
        add_image(args.add)

    
if __name__ == "__main__":
    main()
    