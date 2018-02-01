#!/usr/bin/env python
import asyncio
import logging
from queue import Queue, Empty
from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream import scheduler
from sleekxmpp.exceptions import IqError, IqTimeout

# logging
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')

# your xmpp user
XMPP_JID = "your@jabberuser.com"
XMPP_PWD = "pwd"

# queue for xmpp client thread
xmpp_queue = Queue()

class EchoBot(ClientXMPP):

    def __init__(self, jid, password, loop, msg_callback, queue):
        ClientXMPP.__init__(self, jid, password)

        # asyncio loop and callback
        self.loop = loop
        self.msg_callback = msg_callback
        self.queue = queue

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

    def send_reply(self, msg):
        msg.send()

    def from_main_thread_nonblocking(self):
        try:
            msg = self.queue.get(False) #doesn't block
            logging.info("got msg from main: %s" % msg)
            # schedule the reply
            scheduler.Task("SEND REPLY", 0, self.send_reply, (msg,)).run()
        except Empty:
            pass

    def session_start(self, event):
        self.send_presence()
        # start a scheduler to check the queue
        self.scheduler.add("asyncio_queue", 2, self.from_main_thread_nonblocking,
            repeat=True, qpointer=self.event_queue)

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            # msg received, call the msg callback in the main thread with the event loop
            self.loop.call_soon_threadsafe(self.msg_callback, msg)

def start_sleekxmpp(xmpp_jid, xmpp_pwd, loop, msg_callback, xmpp_queue):
    xmpp = EchoBot(xmpp_jid, xmpp_pwd, loop, msg_callback, xmpp_queue)
    xmpp.connect()
    xmpp.process() # non-blocking!

@asyncio.coroutine
def do_something_async(msg):
    xmpp_queue.put(msg)
    return True

def xmpp_callback(msg):
    msg.reply("I SAW THE LOOP: %(body)s" % msg)
    asyncio.Task(do_something_async(msg))

if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    # call the method to start the EchoBot, use xmpp_callback
    # and xmpp_queue to communicate
    loop.run_in_executor(None, start_sleekxmpp, XMPP_JID, XMPP_PWD,
                         loop, xmpp_callback, xmpp_queue)

    loop.run_forever()
    loop.close()

