#!/usr/bin/env python
import datetime
import json

import gtk
import gobject

# TODO: fix gi.repository.WebKit to have a working webview.get_dom_document
import webkit

# This is a module providing direct python bindings into JavaScriptCore.
# http://packages.linuxdeepin.com/deepin/pool/main/p/python-javascriptcore/python-javascriptcore_0.0003-deepin1_amd64.deb
import javascriptcore

# This is another JavaScriptCore library. It doesn't support python callbacks.
# import jswebkit as javascriptcore

import pymongo

class WebView(webkit.WebView):
    """
    Manage the actual webpage and the interface to the webpage here.
    """

    __gsignals__ = {
        "started": (gobject.SIGNAL_RUN_FIRST,
                    gobject.TYPE_NONE,
                    (gobject.TYPE_OBJECT,),
                   )
    }

    def __init__(self, browser):
        super(WebView, self).__init__()

        # keep a reference to the parent object
        self._browser = browser

        self.results = []
        self.resultcounter = 0
        self.last_balance = 0
        self.last_invested = 0

        self.settings = self.get_settings()

        self.settings.set_property("enable-java-applet", False)
        self.settings.set_property("enable-plugins", False)
        self.settings.set_property("enable-scripts", True)

        self.settings.set_property("enable-file-access-from-file-uris", True)

        self.settings.set_property("enable-private-browsing", False)
        self.settings.set_property("enable-spell-checking", False)
        self.settings.set_property("enable-universal-access-from-file-uris", True)
        self.settings.set_property("enable-dns-prefetching", True)
        self.settings.set_property("enable-webaudio", True)
        self.settings.set_property("enable-webgl", True)
        self.settings.set_property("enable-fullscreen", True)
        self.settings.set_property("enable-xss-auditor", False)
        self.settings.set_property("javascript-can-open-windows-automatically", False)

        self.settings.set_property("user-agent", Browser.user_agent)

        #self.set_full_content_zoom(True)
        self.set_border_width(0)
        self.set_custom_encoding('UTF-8')

        self.set_double_buffered(True)
        self.set_transparent(True)
        self.set_editable(False)
        #self.set_view_mode(False)
        self.set_view_source_mode(False)

        self.console_response = self.connect('console-message', self.on_console_message)
        self.connect('notify::load-status', self._on_load_status)

        # HACK to get JSGlobalContextRef
        #self.connect("window-object-cleared", self.on_window_object_cleared)

        #self.connect('load-finished', self.on_load_finished)
        self.connect("document-load-finished", self.on_load_finished)

    def _on_load_status(self, view, browser):
        if view.get_property('load-status') == webkit.LOAD_FINISHED:
            print ('* Browser load finished')
            # This needs to run with a timeout because otherwise the
            # status is emited before the offscreen image is finished.
            # GObject.timeout_add(100, lambda: self.emit("render-finished"))
        elif view.get_property('load-status') == webkit.LOAD_FAILED:
            print ('* Browser load failed')
        elif view.get_property('load-status') == webkit.LOAD_COMMITTED:
            print ('* Browser load commited')
        elif view.get_property('load-status') == webkit.LOAD_PROVISIONAL:
            print ('* Browser load provisional')
        elif view.get_property('load-status') == webkit.LOAD_FIRST_VISUALLY_NON_EMPTY_LAYOUT:
            print ('* Browser load provisional')

    def on_load_finished(self, browser, web_frame):
        print ('=> event load finished ') #, browser, web_frame
        print ('Provisonal data source:', web_frame.get_provisional_data_source())
        print ('Title:', web_frame.get_title())
        print ('URI:', web_frame.get_uri())

        # add a chat message to the message box (does not send network packets)
        # js.globalObject.socket.listeners("chat").values()[0]("hi world", "500")
        # js.globalObject.socket.emit("chat", js.globalObject.csrf, "hello cruel world")

        self.setup_js()

        print "on_load_finished returning early for testing purposes"
        return

        # let's setup the callbacks
        self.element_bankroll = self.js.globalObject.document.getElementsByClassName("bankroll").values()[0]

        def on_updated_bankroll(whatever):
            self.invested = self.element_bankroll.innerText
            #print "invested: " + str(self.invested)

        self.element_bankroll.addEventListener("DOMSubtreeModified", on_updated_bankroll)

        self.element_investment_profit = self.js.globalObject.document.getElementsByClassName("sprofitpct").values()[0]

        def on_updated_investment_profit(whatever):
            self.investment_profit = self.element_investment_profit.innerText
            #print "investment profit: " + str(self.investment_profit)
        self.element_investment_profit.addEventListener("DOMSubtreeModified", on_updated_investment_profit)

        def on_updated_investment(whatever):
            self.invested = float(self.element_invested.innerText)
        self.element_invested = self.js.globalObject.document.getElementsByClassName("investment").values()[0]
        self.element_invested.addEventListener("DOMSubtreeModified", on_updated_investment)

        def on_updated_balance(whatever):
            self.balance = float(self.element_balance.value)
        self.element_balance = self.js.globalObject.document.getElementById("pct_balance")
        self.element_balance.addEventListener("DOMSubtreeModified", on_updated_balance)

        def on_result(data):
            """
            Bet result data.
            """
            data = dict(data.items())
            data["stats"] = dict(data["stats"].items())
            self._browser.mongo_collection.insert(data)

            if len(self.results) > 1000:
                del self.results[0]

            self.results.append(data)
            self.resultcounter += 1

        self.jscallbacks.on_result = on_result

        self.js.evaluateScript("var on_result = function(data) { return jscallbacks.on_result(data); };")
        self.js.evaluateScript("socket.on('result', on_result);")

        #self.js.globalObject.socket.on("result", self.jscallbacks.on_result)

        # remove the default listener for "timeout"
        self.js.globalObject.socket.removeAllListeners("timeout")

        def on_connection_timeout():
            """
            The webpage eventually disconnects you.
            """
            print "reconnecting at " + str(datetime.datetime.now())
            self.js.evaluateScript("socket.emit('reconnect', csrf);")

        self.jscallbacks.on_connection_timeout = on_connection_timeout
        self.js.evaluateScript("var on_connection_timeout = function() { return jscallbacks.on_connection_timeout(); };")
        self.js.evaluateScript("socket.on('timeout', on_connection_timeout);")

    def on_console_message(self, *args):
        (view, message, line, file) = args
        print ('browser: ' + str(message) + ' in file: ' + str(file) + ' line:' + str(line))
        self.stop_emission('console-message')

    def invest(self):
        print "investing: " + str(self.balance)
        self.last_invested = self.balance
        self.js.evaluateScript("socket.emit('invest', csrf, document.getElementById('pct_balance').value);")

    def divest(self):
        print "divesting: " + str(self.invested)
        print "investment was: " + str(self.last_invested)
        print "difference is: " + str(self.invested - self.last_invested)
        self.element_invested = self.js.globalObject.document.getElementsByClassName("investment").values()[0]
        self.js.evaluateScript("socket.emit('divest', csrf, document.getElementByClassName('investment')[0].innerText);")

    @property
    def profit(self):
        return self.invested - self.last_invested

    def login(self, username, password):
        """
        Send a login signal to the site. This is problematic because it causes
        the page to refresh. Why not just send the cookie the first time?
        """
        self.js.globalObject.socket.emit("login", self.js.globalObject.csrf, username, password)

    def setup_js(self):
        """
        Setup the javascript bindings.
        """

        context = self.get_main_frame().get_global_context()
        # self._js = jswebkit.JSContext(context)
        self._js = javascriptcore.JSContext(context)
        self.document = self._js.evaluateScript("document")

        # setup a JSObject to attach python callbacks to
        self.jscallbacks = self._js.evaluateScript("var jscallbacks = {}; jscallbacks")

        def example(text):
            return text

        self.jscallbacks.example = example
        # js.evaluateScript("jscallbacks.example('500');")

        return self._js

    @property
    def js(self):
        if not hasattr(self, "_js"):
            self.setup_js()
        return self._js

class Browser(object):
    """
    This is the main core of the application. Connects to just-dice.com and
    starts monitoring all data events.
    """

    default_width = 320
    default_height = 240

    user_agent = "NSA"

    def __init__(self):

        self.mongo_client = pymongo.MongoClient()
        self.mongo_db = self.mongo_client.db_justdice
        self.mongo_collection = self.mongo_db.collection_justdice

        self.window = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_default_size(Browser.default_width, Browser.default_height)
        self.window.connect("destroy", self.on_quit)

        #self.vbox = Gtk.VBox()

        self.webview = WebView(self)

        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.add(self.webview)

        self.window.add(self.scrolled_window)
        self.window.show_all()

        #self.webview.load_string(init_string, "text/html", "utf-8", "#")
        #doc = self.webview.get_dom_document()

        # open the main site
        self.webview.open("https://just-dice.com/")
        #self.webview.open("http://diyhpl.us/~bryan/debug.html")

    def on_quit(self, widget):
        gtk.main_quit()

if __name__ == "__main__":
    browser = Browser()

    from IPython.lib.inputhook import enable_gtk
    enable_gtk()

    # Main loop has been replaced by gtk.main() in __main__
    #mainloop = GLib.MainLoop()
    #mainloop.run()
    #mainloop.quit()

    #gtk.main()