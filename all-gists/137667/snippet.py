#
# Get web page screenshot
#
# usage:
#   xvfb-run -s "-screen 0 1024x768x24" python getschreenshot.py test.html
#
# libs:
# - pygtk: http://www.pygtk.org/
# - pywebkitgtk(python-webkit): http://code.google.com/p/pywebkitgtk/
# - PIL: http://www.pythonware.com/products/pil/

#import pygtk
#pygtk.require("2.0")

import gtk
import webkit
import Image

def loaded_handler(thumsize, thumfile):
    def loaded(view, frame):
        try:
            width, height = view.window.get_size()
            # see: http://www.pygtk.org/docs/pygtk/class-gdkpixbuf.html
            pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                    False, 8, width, height)
            pixbuf.get_from_drawable(view.window, view.window.get_colormap(),
                                     0, 0, 0, 0, width, height)
            # pixbuf.save("screenshot.jpg", "jpeg", {"quality": "100"})
            # pixbuf.save("screenshot.png", "png")
            image = Image.fromstring("RGB", (width, height),
                                     pixbuf.get_pixels())
            image.thumbnail(thumsize, Image.ANTIALIAS)
            image.save(thumfile)
            pass
        except:
            import traceback
            traceback.print_exc()
            pass
        gtk.main_quit()
        pass
    return loaded

def print_body(url, thumsize, thumfile, font):
    gtk.gdk.threads_init()
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.move(0, 0)
    window.resize(gtk.gdk.screen_width(), gtk.gdk.screen_height())
    webview = webkit.WebView()

    # webkit settings
    settings = webkit.WebSettings()
    settings.set_property("serif-font-family", font)
    settings.set_property("sans-serif-font-family", font)
    settings.set_property("monospace-font-family", font)
    settings.set_property("default-font-family", font)
    settings.set_property("default-font-size", 14)
    webview.set_settings(settings)

    window.add(webview)
    webview.connect("load-finished", loaded_handler(thumsize, thumfile))
    webview.open(url)
    window.show_all()
    gtk.main()
    pass

if __name__ == "__main__":
    thumsize = (200, 150)
    thumfile = "screenshot.png"
    font = "VLGothic"

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-s", "--size", dest="size",
                      help="output image size", default="%d,%d" % thumsize)
    parser.add_option("-o", "--output", dest="output",
                      help="output image filename", default=thumfile)
    parser.add_option("-f", "--font", dest="font",
                      help="text font", default=font)

    opts, args = parser.parse_args()
    url = args[-1]
    thumfile = opts.output
    try: thumsize = eval(opts.size)
    except: pass

    if not url.startswith("http"): url = "file://" + url
    print_body(url, thumsize, thumfile, font)
    pass

