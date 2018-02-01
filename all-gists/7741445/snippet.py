#!/usr/bin/env python
# -*- coding: utf-8 -*-
# glenn@sensepost.com / @glennzw
# Handle wireless networking from Python
# The name (evil.py) is a play on 'wicd'
from subprocess import Popen, call, PIPE
import errno
from types import *
import logging
import sys
import logging
import time
import argparse
import re
import shlex

SUPPLICANT_LOG_FILE = "wpa_supplicant.log"

"""
This bit of code allows you to control wireless networking
via Python. I chose to encapsualte wpa_supplicant because
it has the most consistent output with greatest functionality.

Currently supports OPEN, WPA[2], and WEP.

#e.g:

>>> iface = get_wnics()[0]
>>> start_wpa(iface)
>>> networks = get_networks(iface)
>>> connect_to_network(iface, "myHomeNetwork", "WPA", "singehackshackscomounaniña")
>>> is_associated(iface)
True
>>> do_dhcp(iface)
>>> has_ip(iface)
True

"""

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(filename)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='evil.log',
                    filemode='w')


def run_program(rcmd):
    """
    Runs a program, and it's paramters (e.g. rcmd="ls -lh /var/www")
    Returns output if successful, or None and logs error if not.
    """

    cmd = shlex.split(rcmd)
    executable = cmd[0]
    executable_options=cmd[1:]    

    try:
        proc  = Popen(([executable] + executable_options), stdout=PIPE, stderr=PIPE)
        response = proc.communicate()
        response_stdout, response_stderr = response[0], response[1]
    except OSError, e:
        if e.errno == errno.ENOENT:
            logging.debug( "Unable to locate '%s' program. Is it in your path?" % executable )
        else:
            logging.error( "O/S error occured when trying to run '%s': \"%s\"" % (executable, str(e)) )
    except ValueError, e:
        logging.debug( "Value error occured. Check your parameters." )
    else:
        if proc.wait() != 0:
            logging.debug( "Executable '%s' returned with the error: \"%s\"" %(executable,response_stderr) )
            return response
        else:
            logging.debug( "Executable '%s' returned successfully. First line of response was \"%s\"" %(executable, response_stdout.split('\n')[0] ))
            return response_stdout


def start_wpa(_iface):
    """
    Terminates any running wpa_supplicant process, and then starts a new one.
    """
    run_program("wpa_cli terminate")
    time.sleep(1)
    run_program("wpa_supplicant -B -Dwext -i %s -C /var/run/wpa_supplicant -f %s" %(_iface, SUPPLICANT_LOG_FILE))

def get_wnics():
    """
    Kludgey way to get wireless NICs, not sure if cross platform.
    """
    r = run_program("iwconfig")
    ifaces=[]
    for line in r.split("\n"):
        if "IEEE" in line:
            ifaces.append( line.split()[0] )
    return ifaces



def get_networks(iface, retry=10):
    """
    Grab a list of wireless networks within range, and return a list of dicts describing them.
    """
    while retry > 0:
        if "OK" in run_program("wpa_cli -i %s scan" % iface):
            networks=[]
            r = run_program("wpa_cli -i %s scan_result" % iface).strip()
            if "bssid" in r and len ( r.split("\n") ) >1 :
                for line in r.split("\n")[1:]:
                    b, fr, s, f = line.split()[:4]
                    ss = " ".join(line.split()[4:]) #Hmm, dirty
                    networks.append( {"bssid":b, "freq":fr, "sig":s, "ssid":ss, "flag":f} )
                return networks
        retry-=1
        logging.debug("Couldn't retrieve networks, retrying")
        time.sleep(0.5)
    logging.error("Failed to list networks")


def _disconnect_all(_iface):
    """
    Disconnect all wireless networks.
    """
    lines = run_program("wpa_cli -i %s list_networks" % _iface).split("\n")
    if lines:
        for line in lines[1:-1]:
            run_program("wpa_cli -i %s remove_network %s" % (_iface, line.split()[0]))  


def connect_to_network(_iface, _ssid, _type, _pass=None):
    """
    Associate to a wireless network. Support _type options:
    *WPA[2], WEP, OPEN
    """
    _disconnect_all(_iface)
    time.sleep(1)
    if run_program("wpa_cli -i %s add_network" % _iface) == "0\n":
        if run_program('wpa_cli -i %s set_network 0 ssid \'"%s"\'' % (_iface,_ssid)) == "OK\n":
            if _type == "OPEN":
                run_program("wpa_cli -i %s set_network 0 auth_alg OPEN" % _iface)
                run_program("wpa_cli -i %s set_network 0 key_mgmt NONE" % _iface)
            elif _type == "WPA" or _type == "WPA2":
                run_program('wpa_cli -i %s set_network 0 psk "%s"' % (_iface,_pass))
            elif _type == "WEP":
                run_program("wpa_cli -i %s set_network 0 wep_key %s" % (_iface,_pass))
            else:
                logging.error("Unsupported type")
            
            run_program("wpa_cli -i %s select_network 0" % _iface)
            
def is_associated(_iface):
    """
    Check if we're associated to a network.
    """
    if "wpa_state=COMPLETED" in run_program("wpa_cli -i %s status" % _iface):
        return True
    return False

def has_ip(_iface):
    """
    Check if we have an IP address assigned
    """
    status = run_program("wpa_cli -i %s status" % _iface)
    r = re.search("ip_address=(.*)", status)
    if r:
        return r.group(1)
    return False

def do_dhcp(_iface):
    """
    Request a DHCP lease.
    """
    run_program("dhclient %s" % _iface)


def main():
    print "[--- EViL. Python wireless network manager. ---]"
    print "[        glenn@sensepost.com / @glennzw\n"
    parser = argparse.ArgumentParser()
    parser.add_argument("-n","--nics", help="List wireless network interfaces.", action="store_true")
    parser.add_argument("-l","--list", help="List wireless networks (specify adapter).", action="store_true")
    parser.add_argument("-i","--iface", help="Specify interface.")
    parser.add_argument("-c","--connect", help="Connect to network.", action="store_true")
    parser.add_argument("-s","--ssid", help="Specify SSID")
    parser.add_argument("-t","--type", help="Specify network type (OPEN, WEP, WPA, WPA2)")
    parser.add_argument("-p","--passw", help="Specify password or key.")
    args = parser.parse_args()

    if len(sys.argv) < 2:
        print "[!] No options supplied. Try --help."
        sys.exit(-1)

    if args.nics:
        nics = get_wnics()
        if nics:
            print "[+] Available NICs:"
            for nic in get_wnics():
                print nic
        else:
            print "[W] No wireless interfaces found :-("
    elif args.list:
        if not args.iface:
            print "[!] Please specify interface. Use --help for help."
            sys.exit(-1)
        else:
            if args.iface not in get_wnics():
                print "[E] Bad interface! - '%s'" % args.iface
                sys.exit(-1)
            print "[+] Searching for available networks..."
            start_wpa(args.iface)
            networks = get_networks(args.iface)
            if networks:
                networks = sorted(networks, key=lambda k: k['sig']) 
                print "[+] Networks in range:"
                for network in networks:
                    print " SSID:\t%s" % network['ssid']
                    print " Sig:\t%s" % network['sig']
                    print " BSSID:\t%s" % network['bssid']
                    print " Flags:\t%s" % network['flag']
                    print " Freq:\t%s\n" % network['freq']
            else:
                print "[W] No wireless networks detected :-("
    elif args.connect:
        if not args.iface or not args.ssid or not args.type or (args.type != "OPEN" and not args.passw):
            print "[E] Missing options for --connect. Check --help for assistance."
            sys.exit(-1)
        else:
            sys.stdout.write( "[+] Associating to '%s' on '%s' (may take some time)... " % (args.ssid, args.iface))
            sys.stdout.flush()
            if args.iface not in get_wnics():
                print "[E] No such wireless interface! - '%s'" % args.iface
                sys.exit(-1)
            start_wpa(args.iface)
            connect_to_network(args.iface, args.ssid, args.type, args.passw)
            while not is_associated(args.iface):
                time.sleep(1)
            print "Success."
            sys.stdout.write("[+] Requesting DHCP lease... ")
            sys.stdout.flush()
            do_dhcp(args.iface)
            while not has_ip(args.iface):
                time.sleep(1)
            print "Success. (%s)" % has_ip(args.iface)
            print "[+] Associated and got lease. Hoorah."

if __name__ == "__main__":
    main()