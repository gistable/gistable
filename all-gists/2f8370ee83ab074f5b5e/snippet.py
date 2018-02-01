# As the Kivy docs ( http://kivy.org/docs/guide/other-frameworks.html ) state:
# install_twisted_rector must be called before importing and using the reactor.
from kivy.support import install_twisted_reactor
install_twisted_reactor()

from autobahn.twisted.websocket import WebSocketClientProtocol, \
                                       WebSocketClientFactory


class MyKivyClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        self.factory._app.print_message('WebSocket connection open.')
        self.factory._proto = self

    def onMessage(self, payload, isBinary):
        if isBinary:
            self.factory._app.print_message("Binary message received: {0} bytes".format(len(payload)))
        else:
            self.factory._app.print_message("Got from server: {}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        self.factory._app.print_message("WebSocket connection closed: {0}".format(reason))
        self.factory._proto = None


class MyKivyClientFactory(WebSocketClientFactory):
    protocol = MyKivyClientProtocol

    def __init__(self, url, app):
        WebSocketClientFactory.__init__(self, url)
        # While the Kivy app needs a reference to the factory,
        # the factory needs a reference to the Kivy app.
        self._app = app
        # Not sure why/whether _proto is needed?
        self._proto = None


from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from twisted.internet import reactor

class KivyClientApp(App):

    def build(self):
        root = self.setup_gui()
        self.connect_to_server()
        return root

    def setup_gui(self):
        """
        Create a vertical oriented boxlayout that contains two widgets:
        1) a label in which we show text sent/received
        2) a textinput where you can enter text
           to the server.
        """
        self.label = Label(text='Connecting...\n')
        # Just 1 line of text; use 10% of the parent's height.
        self.textbox = TextInput(size_hint_y=.1, multiline=False)
        # When the 'Enter' key is pressed, call the method send_message
        # that is defined below.
        self.textbox.bind(on_text_validate=self.send_message)
        # Create the root widget ...
        self.layout = BoxLayout(orientation='vertical')
        # and add the two child widgets.
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.textbox)
        return self.layout

    def connect_to_server(self):
        """
        Connect to the echoing websocket server.
        """
        # The Kivy app needs a reference to the factory object.
        self._factory = MyKivyClientFactory("ws://localhost:9000", self)
        reactor.connectTCP('127.0.0.1', 9000, self._factory)

    def send_message(self, *args):
        """
        Send the text entered that was entered in the texbox widget.
        """
        msg = self.textbox.text
        proto = self._factory._proto
        if msg and proto:
            proto.sendMessage(msg)

            self.print_message('Sent to server: {}'.format(self.textbox.text))
            self.textbox.text = ""

    def print_message(self, msg):
        self.label.text += msg + '\n'

if __name__ == '__main__':

    import sys
    from twisted.python import log
    log.startLogging(sys.stdout)

    KivyClientApp().run()