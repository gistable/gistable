#!/usr/bin/env python
#DiabloHorn https://diablohorn.com
#raw python pcap creater
#based on
#   http://askldjd.com/2014/01/15/a-reasonably-fast-python-ip-sniffer/
#additional references
#   http://www.kanadas.com/program-e/2014/08/raw_socket_communication_on_li.html

import sys
import time
import struct
import IN
import socket

class PcapWrite:
    def __init__(self, filename):
        self.filed = open(filename,'wb')
        self.__write_header()

    def __write_header(self):
        """
            typedef struct pcap_hdr_s {
                    unsigned int magic_number;   /* magic number */
                    unsigned short version_major;  /* major version number */
                    unsigned short version_minor;  /* minor version number */
                    int  thiszone;       /* GMT to local correction */
                    unsigned int sigfigs;        /* accuracy of timestamps */
                    unsigned int snaplen;        /* max length of captured packets, in octets */
                    unsigned int network;        /* data link type */
            } pcap_hdr;
        """
        self.filed.write(struct.pack('I',0xa1b2c3d4))
        self.filed.write(struct.pack('H',2))
        self.filed.write(struct.pack('H',4))
        self.filed.write(struct.pack('i',0))
        self.filed.write(struct.pack('I',0))
        self.filed.write(struct.pack('I',65535))
        self.filed.write(struct.pack('I',1))

    def write_data(self, data):
        """
            typedef struct pcaprec_hdr_s {
                    unsigned int ts_sec;         /* timestamp seconds */
                    unsigned int ts_usec;        /* timestamp microseconds */
                    unsigned int incl_len;       /* number of octets of packet saved in file */
                    unsigned int orig_len;       /* actual length of packet */
            } pcaprec_hdr;
        """
        self.filed.write(struct.pack('I',int(time.time())))
        self.filed.write(struct.pack('I',0))
        self.filed.write(struct.pack('I',len(data)))
        self.filed.write(struct.pack('I',len(data)))
        self.filed.write(data)

    def close_pcap(self):
        self.filed.close()

class EtherSniff:
    def __init__(self, interface_name, pcapwriter):
        self.iface = interface_name
        self.pcapw = pcapwriter
        self.ins = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3)) #3 = ETH_P_ALL
        #man 7 socket SO_RECVBUF
        self.ins.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 212992)
        self.ins.bind((self.iface, 3))

    def __get_mtu(self):
        #http://stackoverflow.com/a/14012003
        #http://books.google.co.il/books?id=9HGUc8AO2xQC&pg=PA31&lpg=PA31&dq#v=onepage&q&f=false
        maxsize = 9000
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        hostName = "10.234.12.23" #can be any IP
        Port = 9999 #can be any port
        s.connect((hostName, Port))
        s.setsockopt(socket.IPPROTO_IP, IN.IP_MTU_DISCOVER, IN.IP_PMTUDISC_DO)
        try:
            s.send('#' * maxsize)
        except socket.error:
            option = getattr(IN, 'IP_MTU', 14)
            return s.getsockopt(socket.IPPROTO_IP, option)
        else:
            return maxsize


    def recv(self):
        while True:
            #ifacename,protocol_type IP or ARP,in or out,packet_type ETHERNET,hwaddr
            pktdata, sa_ll = self.ins.recvfrom(self.__get_mtu())

            self.pcapw.write_data(pktdata)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print sys.argv[0] + " <interface name> <pcap filename>"
        sys.exit()
    pcapwriter = PcapWrite(sys.argv[2])
    sniffer = EtherSniff(sys.argv[1], pcapwriter)
    try:
        sniffer.recv()
    except KeyboardInterrupt:
        pcapwriter.close_pcap()
