# get this: https://github.com/jedie/python-ping.git
import os
import string
from time import time, sleep
from ping import Ping


class QuietPing(Ping):

    def print_failed(self):
        raise Exception()

    def print_success(self, delay, ip, packet_size, ip_header, icmp_header):
        pass

    def print_start(self):
        pass

hosts = ['google.com', 'jpiworldwide.com']

timeout = 1000            # ms
min_wait_time = 2000      # ms
output = []
# setup our screen
os.system(['clear', 'cls'][os.name == 'nt'])
for host in hosts:
    output.append(string.rjust(host, 15) + " : ...")
for line in output:
        print line
while True:
    start_time = time()
    output = []
    for host in hosts:
        try:
            p = QuietPing(host, timeout, 55)
            delay = p.do()
            output.append(string.rjust(host, 15) +
                " : Ok - " + str(int(delay)))
        except Exception:
            output.append(string.rjust(host, 15) + " : DOWN!")
    os.system(['clear', 'cls'][os.name == 'nt'])
    for line in output:
        print line
    elapsed_time = time() - start_time
    sleep(max((float(min_wait_time) / 1000) - elapsed_time, 0))
