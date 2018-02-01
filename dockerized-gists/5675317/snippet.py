#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
from time import sleep

commands = {}

def command(registry):
    def wrapper(func):
        registry[func.__name__] = func
        return func
    return wrapper

def get_socket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock

@command(commands)
def normal(host, port):
    sock = get_socket(host, port)
    sock.send("GET /garam.py HTTP/1.0\n\n")
    res = sock.recv(2048)
    sock.close()
    print res

@command(commands)
def not_found(host, port):
    sock = get_socket(host, port)
    sock.send("GET / HTTP/1.0\n\n")
    sock.close()

@command(commands)
def long_header(host, port):
    sock = get_socket(host, port)
    sock.send("GET /garam.py HTTP/1.0\n")
    sock.send("\0" * 2048)
    res = sock.recv(2048)
    sock.close()
    print res

@command(commands)
def disconnect(host, port):
    sock = get_socket(host, port)
    sock.close()

@command(commands)
def invalid_header(host, port):
    sock = get_socket(host, port)
    sock.send("GET / HTTP/1.0 XXX")
    sock.close()

@command(commands)
def path_traversal(host, port):
    sock = get_socket(host, port)
    sock.send("GET //etc/passwd HTTP/1.0\n\n")
    res = sock.recv(2048)
    sock.close()
    print res

@command(commands)
def slow_down(host, port):
    sock = get_socket(host, port)
    sleep(10)
    sock.send("GET /garam.py HTTP/1.0\n\n")
    res = sock.recv(2048)
    sock.close()
    print res

if __name__ == '__main__':
    import sys

    command_name = 'normal'
    host = '127.0.0.1'
    port = 8000

    if len(sys.argv) > 1:
        command_name = sys.argv[1]
    if len(sys.argv) > 2:
        host = sys.argv[2]
    if len(sys.argv) > 3:
        port = int(sys.argv[3])

    func = commands[command_name]

    func(host, port)
