#!/usr/bin/env python
"""
web page screenshot by webkit

command usage:
  python webkitscreenshot.py test.html

library usage:
  import webkitscreenshot
  image = webkitscreenshot.screenshot_vfb("file://test.html")
  image.save("screenshot.png")

required libs:
- pygtk: http://www.pygtk.org/
- pywebkitgtk(python-webkit): http://code.google.com/p/pywebkitgtk/
- PIL: http://www.pythonware.com/products/pil/

required tools and resouces:
- Xvfb: if you use virtual framebuffer
- VLGothic: as default truetype font
"""

def screenshot(url, **args):
    """
    get screenshot
    - url: screenshot url (if local file: file://...)
    - font_size: default font size
    - font_default: default font family
    - font_serif: serif font
    - font_sans_serif: sans-serif font
    - font_monospace: monospace font
    - size: tuple (width, height) as image size. fullscreen if None

    - return: PIL Image object
    """
    return _WebKitScreenShot(url, **args).image

def screenshot_vfb(url, **args):
    """
    get screenshot in Xvfb
    - same parameters and results as screenshot()
    - size: (1024, 768) as default
    """
    size = (1024, 768)
    if "size" in args:
        size = args["size"]
        del args["size"]
        pass
    proc, screen = vfb(display_spec="%dx%dx24" % size)
    try:
        return screenshot(url, **args)
    finally:
        proc.terminate()
        pass
    pass

class _WebKitScreenShot(object):
    """
    make fullscreen webkit window, then take screenshot into self.image
    """
    def __init__(self, url,
                 font_size=14,
                 font_default="VLGothic",
                 font_serif="VLGothic",
                 font_sans_serif="VLGothic",
                 font_monospace="VLGothic",
                 size=None):
        import gtk
        import webkit
        gtk.gdk.threads_init()

        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.move(0, 0)
        if not size: size = (gtk.gdk.screen_width(), gtk.gdk.screen_height())
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

        window.add(webview)
        webview.connect("load-finished", self._loaded)
        webview.open(url)
        window.show_all()
        gtk.main()
        gtk.gdk.threads_leave()
        pass

    def _loaded(self, view, frame):
        import gtk
        import Image
        try:
            width, height = view.window.get_size()
            # see: http://www.pygtk.org/docs/pygtk/class-gdkpixbuf.html
            pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                    False, 8, width, height)
            pixbuf.get_from_drawable(view.window, view.window.get_colormap(),
                                     0, 0, 0, 0, width, height)
            self.image = Image.fromstring("RGB", (width, height),
                                     pixbuf.get_pixels())
        except:
            #import traceback
            #traceback.print_exc()
            pass
        gtk.main_quit()
        pass
    pass

def vfb(display_spec="1024x768x24", server=0, screen=0, auto_screen=True):
    """
    run Xvfb and set DISPLAY env
    
    usage:
      proc, screen = xvf()
      import gtk
      ...
      proc.terminate()
    """
    import subprocess
    import os
    while True:
        try:
            devnull = open("/dev/null", "w")
            proc = subprocess.Popen(
                ["Xvfb", ":%d" % server,
                 "-screen", "%d" % screen, display_spec],
                shell=False, stdout=devnull, stderr=devnull)
            os.environ["DISPLAY"] = ":%d.%d" % (server, screen)
            return (proc, screen)
        except:
            #import traceback
            #traceback.print_exc()
            if not auto_screen: break
            screen += 1
            pass
        pass
    pass


def _main():
    thumbsize = (200, 150)
    thumbfile = "screenshot.png"
    font = "VLGothic"

    from optparse import OptionParser
    parser = OptionParser()
    parser.usage += " URL"
    parser.add_option("-s", "--size", dest="size",
                      help="output image size: %d,%d" % thumbsize,
                      default="%d,%d" % thumbsize)
    parser.add_option("-o", "--output", dest="output",
                      help="output image filename: %s" % thumbfile,
                      default=thumbfile)
    parser.add_option("-f", "--font", dest="font",
                      help="default font: %s" % font,
                      default=font)

    opts, args = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        import sys
        sys.exit(-1)
        pass

    thumbfile = opts.output
    try: thumbsize = eval(opts.size)
    except: pass
    url = args[0]
    if not url.startswith("http"): url = "file://" + url

    import Image
    image = screenshot_vfb(url,
                           font_default=font, font_sans_serif=font,
                           font_serif=font, font_monospace=font)
    image.thumbnail(thumbsize, Image.ANTIALIAS)
    image.save(thumbfile)
    pass

if __name__ == "__main__": _main()
