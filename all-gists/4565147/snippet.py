#/usr/bin/env python3
# -*- coding: utf-8 -*-

#           _______  _______  _       _________ _        _______ 
# |\     /|(  ___  )(  ____ )( (    /|\__   __/( (    /|(  ____ \
# | )   ( || (   ) || (    )||  \  ( |   ) (   |  \  ( || (    \/
# | | _ | || (___) || (____)||   \ | |   | |   |   \ | || |      
# | |( )| ||  ___  ||     __)| (\ \) |   | |   | (\ \) || | ____ 
# | || || || (   ) || (\ (   | | \   |   | |   | | \   || | \_  )
# | () () || )   ( || ) \ \__| )  \  |___) (___| )  \  || (___) |
# (_______)|/     \||/   \__/|/    )_)\_______/|/    )_)(_______)
#
# If you use this script, your ISP might think you've got a trojan
# and sandbox you, ban you or whatevery they think is appropriate.
#
# This script collects the Monte Carlo web-server statistic-data by
# connecting to random web-servers and asking it for its name.
# The results are stored in a dictionary with each identification string
# as key and the count of web-servers found as value.

#
# If you want to test the maximum speed / concurrent connections
# remove these lines
#        if hcount > 10000:
#            time.sleep(1)
# and run a process per core on your machine. Processes have to have
# different working directories!
#
# Features:
#
# * Defining maximum number of concurrent connections. This is important
#   for OS X and maybe other BSD based systems. They tend to lockup beyond
#   9000 connections. I even had random reboots on OSX.
# * Linux on the other hand just scales and scales and scales. ;-)
# * I was able to maintain 80'000 connections on linux with four processes
#   -> Then I hit the limit of the upstream-bandwidth at home.
# * It only tries to access valid IPs (ie. ignores private IPs)
# * It dumps snapshots of the collected data every 5000 sucessful connections
# * It uses tornados supercool read_until_regex function
# * IPs are feed to the ioloop by a seperate thread
# * it properly cleanups used connections after 6 seconds
# -> To make the script faster you can reduce this timeout, although then
#    you might miss some slow servers/connections.
# * It locks shared datastructures.
# * I used tornade.gen to write async-code as single function using
#   coroutines. Coroutines are one reason I love lua and python!
#   Async-code gets so much more readable!
# * Its not tested on python2 use python3.2 or higher
# * Use 3to2-3.x to convert the iptools module
#    3to2-3.2 -w
#    python setup.py install
# !! CONFIGURE YOUR OS to the maximum concurrent connections you want
#    test. If the hardlimit is already hight enough the script will
#    set a limit of 10240.
# * Remove the resource.setrlimit code if your OS doesn't support it.
# * It uses closure to settings to callbacks
# * I hope the tornado.iostream methods are threadsafe. In a production system
#   you should definitely move these calls to the main thread.

import tornado.gen
import tornado
from tornado import ioloop
from tornado import iostream
import re
import socket
import sys
import time
import _thread
import pickle
import os
import iptools
import resource
import random

# use sysctl on osx or /etc/security/limits.conf on linux to increase number of
# files
l = resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE, (10240, l[1]))
print(resource.getrlimit(resource.RLIMIT_NOFILE))

print(os.getpid())
print(sys.version)
print("Tornado version: %s" % tornado.version)

t0 = time.time()
random.seed(t0)

# Stores socket information to clear old sockets that haven't been answered
hosts = {}
# Logging the server we have connected
servers_connected = list()
# Count connection tries
count = 0
# The actual anonymous statistics we want to create. This is the raw data, it
# has to be condensed for interesting charts/figures.
webservers = {}
# The hosts dict is accessed by two threads
lock = _thread.allocate_lock()
# The regex to find the server in the headers
find_server = re.compile(b"^.erver: ([^\n\r]+)", re.MULTILINE)


def countinc():
    """Increment count and write status or snapshot the collected data"""
    global count
    global servers_connected
    count += 1
    csuccess = len(servers_connected)
    # Write state to console
    if count % 100 == 0:
        sys.stdout.write("\rDone: %d (%d) success unsaved: %d      " % (
            count,
            len(hosts),
            csuccess
        ))
        sys.stdout.flush()
    # Snapshot the current statistics
    if csuccess > 5000:
        pickle.dump(
            webservers,
            open(
                "webservers.p",
                "wb"
            )
        )
        pickle.dump(
            servers_connected,
            open(
                "servers_connected.p",
                "wb"
            )
        )
        os.rename("webservers.p", "webservers.poc")
        os.rename("servers_connected.p", "servers_connected.%d.poc" % count)
        servers_connected = list()


@tornado.gen.engine
def send_request(host, stream):
    """We use tornado gen to collapse async method calls in one method"""
    # The server type is unknown if we can't parse the headers
    server = [host, "unknown"]
    servers_connected.append(server)
    stream.write(("GET / HTTP/1.0\r\nHost: %s\r\n\r\n" % host).encode())
    data = yield tornado.gen.Task(
        stream.read_until_regex,
        find_server
    )
    m = find_server.search(data)
    if m:
        try:
            server[1] = m.groups()[0].decode()
        except:
            pass
    if server[1] in webservers:
        webservers[server[1]] += 1
    else:
        webservers[server[1]] = 1
    sys.stderr.write("%s\n" % server)
    stream.close()


def close_stream(host, stream):
    """Bookkeeping: delete closed hosts from the dict"""
    lock.acquire()
    try:
        del hosts[host]
    except:
        pass
    lock.release()
    countinc()

# IpRanges to check if we generated an valid IP
# Tip: Use 3to2-3.x to convert the iptools module

classA = iptools.IpRange('1.0.0.0', '126.0.0.0')
classB = iptools.IpRange('128.0.0.0', '191.0.0.0')
classC = iptools.IpRange('192.0.0.0', '223.0.0.0')
privA = iptools.IpRange('10.0.0.0', '10.255.255.255')
privB = iptools.IpRange('172.16.0.0', '172.31.255.255')
privC = iptools.IpRange('192.168.0.0', '192.168.255.255')
max_ip = 2 ** 32


# In python3 this is so much nicer to write!
def int_to_ip(ip):
    """Convert 32-bit integer to an IP"""
    return socket.inet_ntoa(ip.to_bytes(4, 'big'))


def ip_ranges():
    """Generator creates random IPs and yields it if it is valid"""
    while True:
        ip = random.randint(0, max_ip)
        ip = int_to_ip(ip)
        if (
            (
                ip in classA or
                ip in classB or
                ip in classC
            ) and not (
                ip in privA or
                ip in privB or
                ip in privC
            )
        ):
            yield ip


def fill_hosts(nop):
    """Generate IPs and create socket and streams, this runs in a thread"""
    for host in ip_ranges():
        s = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            0
        )
        conn_info = [s, time.time()]
        lock.acquire()
        hosts[host] = conn_info
        hcount = len(hosts)
        lock.release()
        # Delay socket creation if we almost reached the limit
        if hcount > 10000:
            time.sleep(1)
        stream = iostream.IOStream(s)
        conn_info.append(stream)
        # Putting current host and stream into a closure.
        # That's nice and easy.
        stream.set_close_callback(
            lambda host=host, stream=stream:
            close_stream(host, stream)
        )
        stream.connect(
            (host, 80),
            lambda host=host, stream=stream:
            send_request(host, stream)
        )


def socket_cleanup():
    """Cleanup unansered sockets that are older than X seconds.
    This is called async, but in the main thread, therefore want
    can possible go wrong? Well, we have to lock the hosts dict."""
    t1 = time.time()
    lock.acquire()
    for key in hosts:
        tmp_host = hosts[key]
        if t1 - tmp_host[1] > 6:
            try:
                tmp_host[0].shutdown(socket.SHUT_RDWR)
            except:
                pass
            tmp_host[2].close()
            tmp_host[0].close()
    lock.release()
    # Call this again in X seconds
    ioloop.IOLoop.instance().add_timeout(
        time.time() + 4, socket_cleanup
    )

# Start the fill-thread
_thread.start_new_thread(fill_hosts, (None,))
print("Go go go")
# Register the timeout for the cleanup
ioloop.IOLoop.instance().add_timeout(
    time.time() + 4, socket_cleanup
)
# Run the ioloop
ioloop.IOLoop.instance().start()