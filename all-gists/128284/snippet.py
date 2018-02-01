#!/usr/bin/env python
# http://gist.github.com/128284

"""
A WebKit-based site performance test

Usage:

    %prog [options] [http://example.net/ ...]
"""

# Inspired by Paul Hammond's http://www.paulhammond.org/webkit2png

# Copyright (c) 2009 Paul Hammond
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

__version__ = "0.1"

import sys
import optparse
import logging
import random
import time

try:
    from ExceptionHandling import NSExceptionHandler, NSLogAndHandleEveryExceptionMask
    from Foundation import NSObject, NSURL, NSURLRequest, NSMakeRect
    from PyObjCTools import AppHelper
    import AppKit
    import WebKit
except ImportError, e:
    logging.error("FATAL ERROR: Cannot import PyObjC: %s" % e)
    sys.exit(1)

TEST_URL = 'http://www.youtube.com/'

class exc_handler(NSObject):
    """
    This exists so we can catch exceptions raised in e.g. WebKit delegates
    which would otherwise halt processing but not exit the runloop.
    """
    def exceptionHandler_shouldLogException_mask_(self, sender, exception, mask):
        return False

    def exceptionHandler_shouldHandleException_mask_(self, sender, exc, mask):
        logging.error("Exiting due to exception: %s" % exc.reason())
        AppKit.NSApplication.sharedApplication().terminate_(None)
        return True

class AppDelegate (NSObject):
    def applicationDidFinishLaunching_(self, aNotification):
        """
        This is fired immediately after the application starts up. We'll ask
        the delegate to start processing URLs
        """

        webview = aNotification.object().windows()[0].contentView()
        delegate = webview.frameLoadDelegate()
        delegate.target_webview = webview
        delegate.getNextURL()

class WebkitLoad (NSObject, WebKit.protocols.WebFrameLoadDelegate):
    current_url    = None
    current_idx    = 0
    request_count  = 0
    target_webview = None
    start_time     = 0.0
    times          = []

    def webView_didFailLoadWithError_forFrame_(self, webview, error, frame):
        logging.error("Something went wrong: %s " % error.localizedDescription())
        self.getNextURL()

    def webView_didFailProvisionalLoadWithError_forFrame_(self, webview, error, frame):
        logging.error("Something went wrong: %s" % error.localizedDescription())
        self.getNextURL()

    def getNextURL(self):
        self.current_url = self.urls[self.current_idx]

        logging.debug("Loading %s" % self.current_url)

        self.start_time = time.time()

        self.target_webview.mainFrame().loadRequest_(
            NSURLRequest.requestWithURL_(
                NSURL.URLWithString_(self.current_url)
            )
        )

        if self.request_count >= self.options.max_requests:
            if not self.times:
                logging.critical("No pages loaded at all?")
            else:
                total_time = sum(self.times)
                print "Loaded %d pages in %0.2f seconds (avg=%0.2f)" % (
                    self.request_count,
                    total_time,
                    total_time / len(self.times)
                )
            AppKit.NSApplication.sharedApplication().terminate_(None)

        self.request_count += 1

        if self.urls[0] == TEST_URL:
            self.urls.pop(0)
            self.request_count -= 1

        if self.options.random:
            i = random.randint(0, len(self.urls) - 1)
        else:
            i = (self.current_idx + 1) % len(self.urls)

        self.current_idx = i


    def webView_didStartProvisionalLoadForFrame_(self, sender, frame):
        logging.debug("Loading started for %s" % self.current_url)
        self.start_time = time.time()

    def webView_didFinishLoadForFrame_(self, webview, frame):
        # Ignore anything but the top-level frame:
        if frame == webview.mainFrame():
            elapsed = time.time() - self.start_time
            if self.current_url != TEST_URL:
                self.times.append(elapsed)
            logging.info("Loaded %s in %0.1f seconds" % (self.current_url, elapsed))
            self.getNextURL()
        else:
            logging.debug("Sub-frame loaded")

class UIDelegate(NSObject, WebKit.protocols.WebUIDelegate):
    def webView_runJavaScriptAlertPanelWithMessage_initiatedByFrame_(self, webview, message, frame):
        logging.error("JavaScript alert: %s" % message)

    def webView_addMessageToConsole_(self, webview, error_dict):
        try:
            logging.error("Javascript error at %(sourceURL)s line %(lineNumber)d: %(message)s" % error_dict)
        except KeyError:
            logging.error("Javascript error (unknown format): %s" % error_dict)


def main():
    cmdparser = optparse.OptionParser(__doc__.strip(), version="wk-bench %s" % __version__)
    cmdparser.add_option("--debug", action="store_true", help="Display more progress information")
    cmdparser.add_option("-u", "--url_list", help="Specify a list of URLs in a file rather than on the command-line")
    cmdparser.add_option("--requests", dest="max_requests", type="int", default=0, help="How many requests to make")
    cmdparser.add_option("--random", action="store_true", default=False, help="Pick URL randomly rather than in-order")
    (options, url_list) = cmdparser.parse_args()

    if options.url_list:
        url_list = map(str.strip, open(options.url_list).readlines())

    if not url_list:
        cmdparser.print_usage()
        sys.exit(1)

    logging.basicConfig(
        format = "%(asctime)s [%(levelname)s]: %(message)s",
        level  = logging.DEBUG if options.debug else logging.INFO
    )

    if not options.max_requests:
        options.max_requests = len(url_list)

    if options.max_requests < len(url_list):
        logging.warn("Making only %d requests even though you provided %d URLs" % (options.max_requests, len(url_list)))

    # Insert a URL which will be used to get all of the actual WebKit
    # initialization out of the way before we load the test sites
    url_list.insert(0, TEST_URL)

    app = AppKit.NSApplication.sharedApplication()

    # create an app delegate
    delegate = AppDelegate.alloc().init()
    AppKit.NSApp().setDelegate_(delegate)

    # create a window
    rect = NSMakeRect(0, 0, 1024, 768)
    win = AppKit.NSWindow.alloc()
    win.initWithContentRect_styleMask_backing_defer_ (rect, AppKit.NSBorderlessWindowMask, 2, 0)

    if options.debug:
        win.orderFrontRegardless()

    # create a webview object
    webview = WebKit.WebView.alloc()
    webview.initWithFrame_(rect)

    webview.setPreferencesIdentifier_('wk-bench')

    win.setContentView_(webview)

    load_delegate = WebkitLoad.alloc().init()
    load_delegate.options = options
    load_delegate.urls = url_list
    webview.setFrameLoadDelegate_(load_delegate)
    ui_delegate = UIDelegate.alloc().init()
    webview.setUIDelegate_(ui_delegate)

    # Not supported by PyObjC yet:
    # NSSetUncaughtExceptionHandler(exc_handler)
    #
    # Instead we'll install a custom delegate for the ExceptionHandling framework
    # to use. In theory this should include logic to filter events but it appears
    # not to be an issue for an app this primitive in testing
    exc_delegate = exc_handler.alloc().init()
    NSExceptionHandler.defaultExceptionHandler().setDelegate_(exc_delegate)
    NSExceptionHandler.defaultExceptionHandler().setExceptionHandlingMask_(NSLogAndHandleEveryExceptionMask)

    AppHelper.runEventLoop(installInterrupt=True)

if __name__ == '__main__' :
    main()