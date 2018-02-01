#!/usr/bin/env python
#
 
from __future__ import with_statement
import os, urllib2, re, base64
from google.appengine.api import users, images, files
from google.appengine.ext import blobstore, db, webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

class MainHandler(webapp.RequestHandler):
  def get(self):
    ''' stuff '''

class Drawing(db.Model):
  ''' heres a drawing model '''
  user = db.UserProperty()
  created = db.DateTimeProperty(auto_now_add=True)
  blob_key = blobstore.BlobReferenceProperty()


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    self.response.headers["Access-Control-Allow-Origin"] = "*"

    try:
      data = self.request.get('imgdata')
      data_to_64 = re.search(r'base64,(.*)', data).group(1)      
      decoded = data_to_64.decode('base64')

      # Create the file
      file_name = files.blobstore.create(mime_type='image/png')

      # Open the file and write to it
      with files.open(file_name, 'a') as f:
        f.write(decoded)          

      # Finalize the file. Do this before attempting to read it.
      files.finalize(file_name)

      key = files.blobstore.get_blob_key(file_name)
      drawing = Drawing(user = users.get_current_user(),
                        blob_key = key)

      url = 'https://gweb-plusexperiments-exp6.appspot.com/serve/%s' % key
      self.response.out.write('{ "url": "' + url + '" }')

    except Exception, e:      
      print e

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, key):    
    if not blobstore.get(key):
      self.error(404)
    else:
      self.send_blob(key)

face = webapp.WSGIApplication([('/', MainHandler),
                               ('/upload', UploadHandler),
                               ('/test-upload', TestUpload),
                               ('/serve/([^/]+)?', ServeHandler),
                               ], debug=True)
