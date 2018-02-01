import dpkt
import humanfriendly
import nids
import pandas as pd
import socket
import sys

conv = {}
ip_to_domain = {}
end_states = (nids.NIDS_CLOSE, nids.NIDS_TIMEOUT, nids.NIDS_RESET)

def handle_tcp_stream(tcp):
    ports = [80, 443]
    if tcp.addr[1][1] not in ports:
        return
    global conv
    if tcp.nids_state == nids.NIDS_JUST_EST:
        tcp.client.collect = 1
        tcp.server.collect = 1
    elif tcp.nids_state == nids.NIDS_DATA:
        tcp.discard(0)
    elif tcp.nids_state in end_states:
        ip = tcp.addr[1][0]
        conv.setdefault(ip, 0)
        conv[ip] += len(tcp.client.data[:tcp.client.count]) + len(tcp.server.data[:tcp.server.count])

def udp_callback(addrs, payload, pkt):
    if addrs[0][1] != 53:
        return
    dns = dpkt.dns.DNS(payload)
    global ip_to_domain
    for q in dns.qd:
        domain = q.name
        for a in dns.an:
            try:
                ip_to_domain[socket.inet_ntoa(a.ip)] = domain
            except AttributeError:
                pass
    return

def extract(pcap_file):
    nids.param("tcp_workarounds", 1)
    nids.param("scan_num_hosts", 0)          # disable portscan detection
    nids.chksum_ctl([('0.0.0.0/0', False)])  # disable checksumming

    nids.param("filename", pcap_file)
    nids.init()
    nids.register_tcp(handle_tcp_stream)
    nids.register_udp(udp_callback)

    try:
        nids.run()
    except Exception, e:
        print "Exception ", pcap_file + " ", e
    data = []
    columns = ('name', 'bytes', 'human_bytes')
    for ip, byte in conv.iteritems():
        name = ip_to_domain[ip] if ip in ip_to_domain else ip
        data.append([name, byte, humanfriendly.format_size(byte)])
    df = pd.DataFrame(data, columns=columns)
    df = df.sort('bytes', ascending=False)
    return df

if __name__ == "__main__":
    print extract(sys.argv[1])