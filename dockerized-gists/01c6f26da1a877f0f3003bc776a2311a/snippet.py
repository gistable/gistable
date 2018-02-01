#!/usr/bin/env python
# DiabloHorn - https://diablohorn.com
# scan target IP from an interface with no IP configured
# POC - scapy
#   pkt = Ether(dst='00:0c:29:f6:a5:65',src='00:08:19:2c:e0:15') / IP(dst='172.16.218.178',src='172.16.218.255') / TCP(dport=445,flags='S')
#   sendp(pkt,iface='eth0')


import sys
from scapy.all import *
import time
import threading
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class checkreply(threading.Thread):
    def __init__(self, iface, dip, dports):
        self.started = True
        self.iface = iface
        self.dip = dip
        self.dports = dports
        self.portseen = []
        threading.Thread.__init__(self)
    
    def run(self):
        logging.debug('Sniffer thread called')
        sniff(iface=self.iface,store=0,prn=self.checkport,stop_filter=self.stopflag,filter="tcp and host {0}".format(self.dip))
    
    def checkport(self,pktdata):
        logging.debug('Sniffer packet inspection triggered')
        if pktdata.haslayer(TCP):
            tcpdata = pktdata.getlayer(TCP)
            #check if syn and ack flags are set
            if tcpdata.sport not in self.portseen:
                if ((tcpdata.flags >> 1) & 1) and ((tcpdata.flags >> 4) & 1):
                    if tcpdata.sport in self.dports:
                        logging.info('Found open port - %s' % tcpdata.sport)
                        self.portseen.append(tcpdata.sport)         
                #check if reset flag set
                if ((tcpdata.flags >> 2) & 1):
                    if tcpdata.sport in self.dports:
                        logging.info('Found closed port - %s' % tcpdata.sport)
                        self.portseen.append(tcpdata.sport)
                    
    def stopflag(self, pktdata):
        logging.debug('Sniffer thread check stop flag')
        if self.started:
            return False
        return True
            
    def stopsniffer(self):
        self.started = False
           
def convert2bcast(ip):
    parts = ip.split('.')
    parts[3] = 255
    return '.'.join(str(x) for x in parts)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='port scan target IPs from interface without IP assigned')
    parser.add_argument('targetip',type=str,help='target ip to perform port scan on')
    parser.add_argument('targetmac',type=str,help='target MAC address of IP')
    parser.add_argument('-i', '--iface',type=str,required=True,help='network interface to use')
    parser.add_argument('-p', '--ports',nargs='+',type=int,required=True,help='space separated list of ports')
    parser.add_argument('-m', '--smac',type=str,help='mac address used to send packets, defaults to current')
    myargs = parser.parse_args()

    logging.info('Started ipless port scan')

    #https://stackoverflow.com/a/32080877
    if myargs.smac is None:
        with open('/sys/class/net/{0}/address'.format(myargs.iface),'r') as macfile:
            myargs.smac = macfile.readline().strip()
    
    replychecker = checkreply(myargs.iface,convert2bcast(myargs.targetip),myargs.ports)
    replychecker.start()
    logging.info('Started sniffer and waiting 10s')
    time.sleep(10)
    logging.info('Starting port scan')
    for port in myargs.ports:
        logging.debug('Scanning port - %s' % port)
        pkt = Ether(dst='{0}'.format(myargs.targetmac),src='{0}'.format(myargs.smac)) / IP(dst='{0}'.format(myargs.targetip),src='{0}'.format(convert2bcast(myargs.targetip))) / TCP(dport=port,flags='S')
        sendp(pkt,verbose=False)
    logging.info('Finished port scan, waiting 5s for packets')
    time.sleep(5)
    replychecker.stopsniffer()
    replychecker.join()
    logging.info('Stopped sniffer')