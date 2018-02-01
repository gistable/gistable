# -*- coding: utf-8 -*-
from plugpy.ext.skype import SimpleSkypePlugin 
import itertools
import mimetools
import mimetypes
from cStringIO import StringIO
import urllib2
import os
import feedparser
from pyquery import PyQuery as pq
import random
import tempfile
import Image

url = "http://pinkimg.blog57.fc2.com/?xml"


class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return
    
    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return
    
    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts = []
        part_boundary = '--' + self.boundary
        
        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )
        
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )
        
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)

def get_entries():
    urls = []
    d = feedparser.parse(url)
    for a in d.entries:
        urls.append(a.link)
    return urls

def get_image_list(url):
    urls = []
    conn = urllib2.urlopen(url)
    page = conn.read()
    d = pq(page)
    for a in d(".entry_text img"):
        src = pq(a).attr.src
        if src.endswith("s.jpg"):
            urls.append(src)
    return urls

def download(urls):
    imgs = []
    for url in urls:
        conn = urllib2.urlopen(url)
        data = conn.read()
        f = tempfile.TemporaryFile()
        f.write(data)
        f.flush()
        f.seek(0)
        img = Image.open(f)
        imgs.append(img)
    return concat_img(imgs)

def concat_img(imgs):
    w = max(i.size[0] for i in imgs)
    h = sum(i.size[1] for i in imgs)

    result = Image.new("RGBA", (w, h))

    y = 0
    for i in imgs:
        result.paste(i, (0, y))
        y += i.size[1]

    return result

def get_concat_image(): 
    urls = get_entries()
    url = random.choice(urls)
    image_urls = get_image_list(url)
    return download(image_urls)

def pink2gyazo():
    image = get_concat_image()
    import tempfile
    tmp = tempfile.TemporaryFile()
    image.save(tmp, "png")
    tmp.seek(0)

    form = MultiPartForm()
    form.add_field('id', '')
    
    form.add_file('imagedata', 'gyazo.com', 
                  fileHandle=tmp)

    request = urllib2.Request('http://gyazo.com/upload.cgi')
    request.add_header('User-agent', 'Gyazo/1.0)')
    body = str(form)
    request.add_header('Content-type', form.get_content_type())
    request.add_header('Content-length', len(body))
    request.add_data(body)

    return urllib2.urlopen(request).read()


class PinkPlugin(SimpleSkypePlugin):

    alias = "#pink"

    def on_message(self, *args):
        return u"これでヌイてね %s" % pink2gyazo()

