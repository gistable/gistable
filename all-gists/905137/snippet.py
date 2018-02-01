#!/usr/bin/env python

import itertools
import mimetools
import mimetypes
from cStringIO import StringIO
import urllib
import urllib2
import gtk

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




def screenshot(url, **args):
    return WebKitScreenShot(url, **args).image


class WebKitScreenShot(object):
    """
    make fullscreen webkit window, then take screenshot into self.image
    """
    def __init__(self, url=None,
                 font_size=14,
                 font_default="VLGothic",
                 font_serif="VLGothic",
                 font_sans_serif="VLGothic",
                 font_monospace="VLGothic",
                 size=None):
        import webkit
        gtk.gdk.threads_init()
        #gtk.gdk.threads_enter()

        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        scr = gtk.ScrolledWindow()
        window.move(0, 0)
        if not size: 
            size = (gtk.gdk.screen_width(), gtk.gdk.screen_height())
        window.resize(*size)
        webview = webkit.WebView()

        # webkit settings
        settings = webkit.WebSettings()
        settings.set_property("serif-font-family", font_serif)
        settings.set_property("sans-serif-font-family", font_sans_serif)
        settings.set_property("monospace-font-family", font_monospace)
        settings.set_property("default-font-family", font_default)
        settings.set_property("default-font-size", font_size)
        webview.set_settings(settings)
        
        #window.add(scr)
        #scr.add(webview)
        
        window.add(webview)
        
        webview.connect("load-finished", self._loaded)
        webview.open(url)
        self.webview = webview
        window.show_all()
        self.window = window
        gtk.main()
        gtk.gdk.threads_leave()


    def _loaded(self, view, frame):
        gtk.gdk.threads_enter()
        #import gtk
        import Image
        try:
            #print dir(frame.get_global_context())
            pixmap = view.get_snapshot()

            #print pixmap.get_size() 
            
            width, height = view.window.get_size()
            # see: http://www.pygtk.org/docs/pygtk/class-gdkpixbuf.html
            pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                    False, 8, width, height)
            #pixbuf.get_from_drawable(view.window, view.window.get_colormap(),
            pixbuf.get_from_drawable(pixmap, view.window.get_colormap(),
                                     0, 0, 0, 0, width, height)
            self.image = Image.fromstring("RGB", (width, height),
                                     pixbuf.get_pixels())
            gtk.main_quit()
        except:
            import traceback
            traceback.print_exc()
        gtk.gdk.threads_leave()


def check_url(url):
    from urlparse import urlparse
    ret = urlparse(url)
    scheme = ret.scheme
    if scheme not in ["http", "https"]:
        return False
    hostname = ret.hostname
    if hostname.startswith("192.168"):
        return False
    return True

def gyazo(url):
    if not check_url(url):
        print "Permission denied"
        return
    font = "VLGothic"
    import Image
    image = screenshot(url,
                           font_default=font, font_sans_serif=font,
                           font_serif=font, font_monospace=font)
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

    print urllib2.urlopen(request).read()

if __name__ == '__main__':

    from optparse import OptionParser
    parser = OptionParser()
    parser.usage += " URL"

    opts, args = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        import sys
        sys.exit(-1)

    url = args[0]
    gyazo(url)




