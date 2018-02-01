import collections
import threading

__author__ = 'ashw7n'

import socket
import json
import logging

logging.basicConfig(level=logging.DEBUG)


OVSDB_IP = '192.168.111.135'
OVSDB_PORT = 5000

"""
a simple client to talk to ovsdb over json rpc
"""


def default_echo_handler(message, ovsconn):
    logging.debug("responding to echo")
    ovsconn.send({"result": message.get("params", None),
                  "error": None, "id": message['id']})

def default_message_handler(message, ovsconn):
    logging.debug("default handler called for method %s", message['method'])
    ovsconn.responses.append(message)

class OVSDBConnection(threading.Thread):
    """Connects to an ovsdb server that has manager set using

        ovs-vsctl set-manager ptcp:5000

        clients can make calls and register a callback for results, callbacks
         are linked based on the message ids.

        clients can also register methods which they are interested in by
        providing a callback.
    """

    def __init__(self, IP, PORT, **handlers):
        super(OVSDBConnection, self).__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((IP, PORT))
        self.responses = []
        self.callbacks = {}
        self.read_on = True
        self.handlers = handlers or {"echo": default_echo_handler}
        self.start()

    def send(self, message, callback=None):
        if callback:
            self.callbacks[message['id']] = callback
        self.socket.send(json.dumps(message))

    def response(self, id):
        return [x for x in self.responses if x['id'] == id]

    def set_handler(self, method_name, handler):
        self.handlers[method_name] = handler

    def _on_remote_message(self, message):
        logging.debug("message %s", message)
        try:
            json_m = json.loads(message,
                                object_pairs_hook=collections.OrderedDict)
            #check first to see if the message is for a method and we have a
            # handler for it
            handler_method = json_m.get('method', None)
            if handler_method:
                self.handlers.get(handler_method, default_message_handler)(
                    json_m, self)
            elif json_m.get("result", None) and json_m['id'] in self.callbacks:
                id = json_m['id']
                #check if this is a result of an earlier call we made and that
                # we have a callback registered
                if not self.callbacks[id](json_m, self):
                    # if callback is to be persisted, callback should return
                    # something
                    self.callbacks.pop(id)

            else:
                #add it for sync clients
                default_message_handler(message, self)
        except Exception as e:
            logging.exception("exception [%s] while handling message [%s]", e.message, message)

    def __echo_response(message, self):
        self.send({"result": message.get("params", None),
                   "error": None, "id": message['id']})

    def run(self):

        chunks = []
        lc = rc = 0
        while self.read_on:
            response = self.socket.recv(4096)
            if response:
                response = response.decode('utf8')
                message_mark = 0
                for i, c in enumerate(response):
                    #todo fix the curlies in quotes
                    if c == '{':
                        lc += 1
                    elif c == '}':
                        rc += 1

                    if rc > lc:
                        raise Exception("json string not valid")

                    elif lc == rc and lc is not 0:
                        chunks.append(response[message_mark:i + 1])
                        message = "".join(chunks)
                        self._on_remote_message(message)
                        lc = rc = 0
                        message_mark = i + 1
                        chunks = []

                chunks.append(response[message_mark:])

    def stop(self, force=False):
        self.read_on = False
        if force:
            self.socket.close()


if __name__ == '__main__':

    # E.g of setting a custom handler
    # def custom_echo_handler(message, ovsconn):
    #     print "handling echo..."
    #     ovsconn.send({"result": message.get("params", None),
    #                       "error": None, "id": message['id']})
    #
    # ovsdb = OVSDBConnection(OVSDB_IP, OVSDB_PORT, echo=custom_echo_handler)

    ovsdb = OVSDBConnection(OVSDB_IP, OVSDB_PORT)

    # E.g setting a callback and making a call. Note that the callback has to
    # set everytime unless the callback returns a truth value (True)
    def res(message, ovsconn):
        print "list_dbs_query response ", json.dumps(message)

    # #with callback
    list_dbs_query = {"method": "get_schema", "params": ['Open_vSwitch'],
                      "id": 0}
    ovsdb.send(list_dbs_query, res)

    def monitor_res(message, ovsconn):
        print "monitor response", json.dumps(message)
        return True  # we want to persist this callback

    monitor_message = {'id': 100, 'method': 'monitor', 'params': ['Open_vSwitch', None, {
        'Bridge': [{'select': {'initial': True, 'insert': True, 'delete': True,
                               'modify': True}}]}]}
    ovsdb.set_handler("update", monitor_res)
    ovsdb.send(monitor_message, monitor_res)


