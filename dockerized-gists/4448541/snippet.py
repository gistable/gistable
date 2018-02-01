# okcupidgirl.py ignores you
from __future__ import print_function
import argparse
import socket
import select


def listen(port):
    print("Listening on port {}".format(port))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind(("", port))
    server.listen(1)
    inputs = [server]
    outputs = []
    while True:
        ready, _, _ = select.select(inputs, outputs, inputs)
        for s in ready:
            if s is server:
                conn, addr = s.accept()
                conn.setblocking(0)
                inputs.append(conn)
                print("Accepting connection from ", addr)
            else:
                data = s.recv(1024)
                if data:
                    print("Ignoring data from ", s.getpeername(), ": ", data)
                else:
                    print("Closing connection from ", s.getpeername())
                    s.close()
                    inputs.remove(conn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Accept connections, never reply')
    parser.add_argument("port", type=int)
    args = parser.parse_args()

    listen(args.port)