#!/usr/bin/env python

"""
An example demonstrating how to use xpyb (xcb bindings for Python) to take a
full-screen screenshot.
"""

# Meta
__version__ = '1.0'
__version_info__ = (1, 0)
__license__ = "Apache 2.0"
__author__ = 'Dan McDougall <daniel.mcdougall@liftoffsoftware.com>'

# Stdlib imports
import sys, os

# 3rd party imports
import xcb, xcb.xproto
import Image # PIL (I also recommend Pillow which is 100% compatible with PIL)

def xcb_screenshot_full(conn, path="/tmp/screenshot.png"):
    """
    Given an XCB connection (*conn*), saves a full-screen screenshot to *path*.
    """
    # XCB boilerplate stuff:
    setup = conn.get_setup()
    screen = setup.roots[0]
    width = screen.width_in_pixels
    height = screen.height_in_pixels
    root = screen.root
    # GetImage requires an output format as the first arg.  We want ZPixmap:
    output_format = xcb.xproto.ImageFormat.ZPixmap
    plane_mask = 2**32 - 1 # No idea what this is but it works!
    reply = conn.core.GetImage(
        output_format, root, 0, 0, width, height, plane_mask).reply()
    # The reply contains the image data in ZPixmap format.  We need to convert
    # it into something PIL can use:
    image_data = reply.data.buf()
    im = Image.frombuffer(
        "RGBX", (width, height), image_data, "raw", "BGRX").convert("RGB")
    with open(path, 'w') as f:
        im.save(f, format='png')

if __name__ == "__main__":
    x11_display = os.environ['DISPLAY']
    print("Taking screenshot...")
    try:
        conn = xcb.connect(display=x11_display)
        xcb_screenshot_full(conn)
    except Exception as e:
        print("Got an exception trying to take a screenshot!")
        print("This might be helpful:")
        print(e)
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
    sys.exit(0)