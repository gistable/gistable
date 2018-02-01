'''
Easy Mac
Copyright (2015) Sean Beck
Licensed under Creative Commons Attribution-ShareAlike 4.0 International
See: https://creativecommons.org/licenses/by-sa/4.0/

Easily change your MAC address on Linux using `ifconfig`
'''
#!/usr/bin/python2.7

import argparse
import os
import random
import subprocess
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, help='The interface ID whose MAC you wish to change')
    return parser.parse_args()


def make_mac():
    '''
    Makes the MAC look like a VMware MAC address
    '''
    mac = [
        0x00,
        0x05,
        0x69,
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)
    ]
    return ':'.join('{0:02X}'.format(n) for n in mac)


def set_mac(dev, mac):
    cmd = 'sudo ip link set down dev {}'.format(dev)
    subprocess.call(cmd.split())
    cmd = 'sudo ip link set dev {} address {}'.format(dev, mac)
    subprocess.call(cmd.split())
    cmd = 'sudo ip link set up dev {}'.format(dev)
    subprocess.call(cmd.split())


def get_root():
    euid = os.geteuid()
    if euid != 0:
        print '[-] You didn\'t run as root!'
        print '[-] Exiting...'
        sys.exit(1)


def main():
    get_root()
    args = get_args()
    if not args.d:
        print '[-] Please specify a target device'
        sys.exit(1)
    mac = make_mac()
    print '[+] Generated MAC with value', mac
    set_mac(args.d, mac)
    print '[+] MAC is now changed'


if __name__ == '__main__':
    main()