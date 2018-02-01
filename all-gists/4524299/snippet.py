from netfilterqueue import NetfilterQueue
import subprocess
import signal
import dpkt
import traceback
import socket

def observe_dns_hijacking(nfqueue_element):
    try:
        ip_packet = dpkt.ip.IP(nfqueue_element.get_payload())
        dns_packet = dpkt.dns.DNS(ip_packet.udp.data)
        print(repr(dns_packet))
        for answer in dns_packet.an:
            print(socket.inet_ntoa(answer['rdata']))
        nfqueue_element.accept()
    except:
        traceback.print_exc()
        nfqueue_element.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(0, observe_dns_hijacking)

def clean_up(*args):
    subprocess.call('iptables -D OUTPUT -p udp --dst 8.8.8.8 -j QUEUE', shell=True)
    subprocess.call('iptables -D INPUT -p udp --src 8.8.8.8 -j QUEUE', shell=True)

signal.signal(signal.SIGINT, clean_up)

try:
    subprocess.call('iptables -I INPUT -p udp --src 8.8.8.8 -j QUEUE', shell=True)
    subprocess.call('iptables -I OUTPUT -p udp --dst 8.8.8.8 -j QUEUE', shell=True)
    print('running..')
    nfqueue.run()
except KeyboardInterrupt:
    print('bye')