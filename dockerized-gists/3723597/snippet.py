'''pass_socket.py

Written September 14, 2012

Released into the public domain.

Works on Python 2.6, 2.7, and may need minor changes for 3+.
'''

import multiprocessing
from multiprocessing import reduction
import socket
import time

def worker(conn):
    time.sleep(.5)
    conn.poll(None)
    s = socket.fromfd(reduction.recv_handle(conn), socket.AF_INET, socket.SOCK_STREAM)
    s.sendall('GET /\r\n\r\n')
    d = s.recv(100)
    conn.send(d)
    s.close()

def main():
    parent, child = multiprocessing.Pipe()
    ch = multiprocessing.Process(target=worker, args=(child,))
    ch.start()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('www.google.com', 80))
    while not ch.pid:
        time.sleep(.25)
    reduction.send_handle(parent, s.fileno(), ch.pid)
    s.close()
    time.sleep(1)
    result = parent.recv()
    print result
    ch.join()

if __name__ == '__main__':
    main()
