# Copyright 2009 Daniel Dotsenko dotsa@hotmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import threading

class Base(object):

    def __init__(self, handlers = [], bindings = []):
        self.handlers = handlers
        self.bindings = list(bindings) # we will be rewriting port numbers when port 0 is used for "autoassign"
        self.loop = None

    def _server_runner(self, handlers, bindings, loop):
        raise NotImplementedError("Override _server_runner method in your sub-class.")

    def start(self):

        if not self.handlers or not self.bindings:
            raise ArgumentError("To run a web applicaiton, we need to know the port and have at least one handler.")

        if self.loop and self.loop.running():
            return

        self.loop = IOLoop()

        th = threading.Thread(
            target = self._server_runner
            , args = [
                self.handlers
                , self.bindings
                , self.loop
            ]
        )
        th.daemon = True
        th.start()

    def stop(self):
        logging.debug(HELLO + " stopping")
        # http://www.tornadoweb.org/documentation/ioloop.html
        # "It is safe to call this method from any thread at any time. 
        # Note that this is the only method in IOLoop that makes this guarantee;
        # all other interaction with the IOLoop must be done from that IOLoop’s
        # thread. add_callback() may be used to transfer control from other
        # threads to the IOLoop’s thread."
        loop = self.loop
        self.loop = None

        loop.add_callback(loop.stop)

        try:
            # it's unfortunate that Tornado people used "_" prefix for this.
            # This should be a public API property.
            loop._waker.wake()
        except:
            pass

    @property
    def is_running(self):
        return self.loop and self.loop.running()


class WebApplication(Base):

    def _server_runner(self, handlers, bindings, loop):

        http_server = HTTPServer(
            Application( handlers = handlers )
            , io_loop = loop
        )

        for binding in bindings:
            # for now we just start listenning on all IPs for given port.
            # will wire up domain/ip binding later.
            http_server.listen(binding[1])

        logging.debug(HELLO + "started")
        loop.start()
        # "An IOLoop must be completely stopped before it can be closed. 
        # This means that IOLoop.stop() must be called and IOLoop.start()
        # must be allowed to return before attempting to call IOLoop.close().
        # Therefore the call to close will usually appear just after the call
        # to start rather than near the call to stop"
        logging.debug(HELLO + "stopped")
        loop.close()

if __name__ == '__main__':

    # starting server in a separate thread:

    CWD = os.path.abspath(os.path.dirname(__file__))
    STATIC_FOLDER = 'static'
    PORT = 0 # will be autopicked by the system.
    HANDLERS = [
        (
            r'/web_service/'
            , config_handlers.WebServiceHandler
        ),
        (
            r'/(.*)'
            , StaticFileHandler
            , {'path': os.path.abspath(os.path.join(CWD, STATIC_FOLDER))}
        )
    ]

    server = WebApplication(
        HANDLERS
        , [('', PORT)]
    )

    another_server = WebApplication(
        OTHERHANDLERS
        , [('', OTHERPORT)]
    )

    server.start() # actually started in a sub-thread
    another_server.start() # actually started in a sub-thread

    ev = threading.Event()
    ev.clear()
    try:
        # some non-blocking looping in main thread
        while not ev.isSet():
            print "Main loop"
            ev.wait(30)
    except KeyboardInterrupt:
        pass

    print "good bye"