from sampy import *
import time

import urllib

myhub=SAMPHubProxy()
myhub.connect()

client=SAMPClient(myhub)

metadata1={"samp.name":"Client",
           "samp.description.text":"Client",
           "client.version":"0.01"}

client.start()
client.register()

client.declareMetadata(metadata1)

class Receiver(object):
    def __init__(self):
        self.received = False
    def receive_call(self, private_key, sender_id, msg_id, mtype, params, extra):
        self.private_key = private_key
        self.sender_id = sender_id
        self.msg_id = msg_id
        self.mtype = mtype
        self.params = params
        self.extra = extra
        self.received = True

r = Receiver()

client.bindReceiveCall("table.load.*", r.receive_call)

try:

    while True:
        time.sleep(1)
        if r.received:
            print "Message received"
            break

finally:

    client.unregister()
    client.stop()

    myhub.disconnect()
