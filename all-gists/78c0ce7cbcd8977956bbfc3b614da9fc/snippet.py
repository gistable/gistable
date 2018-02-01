#!/usr/bin/env python3                                                                                                                                 

import argparse
import socket
import pdb
import json
import time
import RPIO
RPIO.setwarnings(False)


# reset if mh drops below this num
min_hashes=185000

# power button press duration to trigger bios shutdown
hold_seconds = 7.5

# how long to stay in power off state
wait_seconds = 5

# time for reboot + claymore to get share and start hashing
loop_seconds = 90

port=3333

def check_rig(host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((host, port))
        print("connected")
        s.send('{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}'.encode("utf-8"))
        j=s.recv(2048)
        s.close()                                                                                                                                      
        resp=json.loads(j.decode("utf-8"))
        resp=resp['result']
        hashes = int(resp[2].split(';')[0])
        print("m/h=" + str(hashes))
        hash_ok=min_hashes < hashes
        print("hashes ok is: " + str(hash_ok))
        return hash_ok
    except TimeoutError:
        print("connection timeout")
    except ConnectionRefusedError:
        print("connection refused")
    except:
        print("exception")

    return False


parser = argparse.ArgumentParser(description='rigmon')
parser.add_argument('--host', action='store', dest="host", default="192.168.2.45", help='hostname of the rig to monitor')
parser.add_argument('--test', action='store_true', dest="test", help='no reset, just dump output')

args = parser.parse_args()

# gpio setup
pin_relay0 = 2
pin_swpwr = pin_relay0
RPIO.setup( pin_relay0, RPIO.OUT)

# main loop
while True:
    if not check_rig(args.host):
        print("resetting rig")
        if not args.test:                                                                                                                              
            RPIO.output(pin_swpwr, 1 )
            time.sleep(hold_seconds)
            RPIO.output(pin_swpwr, 0 )
            print("rig off, waiting to turn on" )
            time.sleep(wait_seconds)
            print("turning rig back on")
            RPIO.output(pin_swpwr, 1 )
            time.sleep(1)
            RPIO.output(pin_swpwr, 0 )
    else:
        print("rig ok!")

    print( "loop sleep" )

    time.sleep(loop_seconds)