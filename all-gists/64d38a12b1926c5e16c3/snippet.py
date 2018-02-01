#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys
import threading


HOST = socket.gethostname()
PORT = 6000


class Server:
    """Server Socket accepts client requests"""
    def __init__(self, host = HOST, port = PORT):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
        except socket.error as msg:
            print 'Error Code: ' + str(msg[0]) + ', Message ' + msg[1]
            sys.exit()
        self.s = s
        t = threading.Thread(target = self.handle_requests)
        t.start()
        self.clients = []

    def handle_requests(self, max_queue = 2):
        self.s.listen(max_queue)
        while True:
            c, addr = self.s.accept()
            self.clients.append(c)

    def send(self, data, client = None):
        if client == None:
            self.clients[0].send(data)
        else:
            client.send(data)

    def receive(self, client = None):
        received_data = ""
        while True:
            if client == None:
                ch = self.clients[1].recv(1)
            else:
                ch = client.recv(1)
            if ch in ('.', 'q'):
                break
            received_data = received_data + ch
        print "\nRECEIVED: " + received_data

    def close():
        self.s.close()


class Client:
    """Client requests server for connection"""
    def __init__(self, host = HOST, port = PORT):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        self.s = s

    def send(self, data):
        self.s.send(data)

    def receive(self):
        received_data = ""
        while True:
            ch = self.s.recv(1)
            if ch in ('\n', '\0', None):
                break
            received_data = received_data + ch
        print "\nRECEIVED: " + received_data

    def close():
        self.c.close()
