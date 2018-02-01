import sys
from scapy.all import *
from scapy.utils import rdpcap


class HttpRequest(object):
    def __init__(self, method, url, version, headers, body):
        self.method = method
        self.url = url
        self.version = version
        self.headers = headers
        self.body = body

    def __repr__(self):
        return '<HttpRequest method=%r url=%r headers=%r body=%r>' % (
            self.method, self.url, self.headers, self.body
        )


class HttpResponse(object):
    def __init__(self, version, code, status, headers, body):
        self.version = version
        self.code = code
        self.status = status
        self.headers = headers
        self.body = body

    def __repr__(self):
        return '<HttpResponse code=%r status=%r headers=%r body=%r>' % (
            self.code, self.status, self.headers, self.body
        )


def interpret_http(p, is_client_packet):
    lines = p.split("\r\n")
    end_of_headers = lines.index('')
    headers = [l.split(': ', 1) for l in lines[1:end_of_headers]]
    start_of_body = sum([len(l) + 2 for l in lines[0:end_of_headers]])
    data = lines[0].split(' ', 2) + [headers, p[start_of_body:]]

    if is_client_packet:
        return HttpRequest(*data)
    else:
        return HttpResponse(*data)


def filter_client_payload(p):
    p.headers = [h for h in p.headers if h[0].lower() in ('authorization', 'content-type')]
    return p


def print_http(pkt_list):
    last_packet_is_client_packet = None
    last_payload = None
    interpreted = []
    for pkt in pkt_list:
        if not pkt[TCP].payload:
            continue

        is_client_packet = (pkt[TCP].dport == 80)
        if last_packet_is_client_packet == is_client_packet:
            last_payload += pkt.payload.load
        else:
            if last_payload is not None:
                interpreted.append(interpret_http(last_payload, last_packet_is_client_packet))
            last_packet_is_client_packet = is_client_packet
            last_payload = pkt.payload.load

    if last_payload is not None:
        interpreted.append(interpret_http(last_payload, last_packet_is_client_packet))

    for http in interpreted:
        if isinstance(http, HttpRequest):
            http = filter_client_payload(http)
        else:
            pass

        print repr(http)


def assemble_sessions(pkts, session_done_cb):
    sessions = {}
    for pkt in pkts:
        if not pkt[TCP]:
            continue
        if pkt[TCP].sport != 80 and pkt[TCP].dport != 80:
            continue

        is_client_packet = (pkt[TCP].dport == 80)

        if is_client_packet:
            session_key = '%s_%d_%s_%d' % (pkt[IP].src, pkt[TCP].sport, pkt[IP].dst, pkt[TCP].dport)
        else:
            session_key = '%s_%d_%s_%d' % (pkt[IP].dst, pkt[TCP].dport, pkt[IP].src, pkt[TCP].sport)
        #print session_key, is_client_packet, pkt[TCP].payload

        if session_key in sessions:
            sessions[session_key].append(pkt)
        else:
            if pkt[TCP].flags == 2 and is_client_packet:  # SYN, initial contact
                sessions[session_key] = [pkt]
            else:
                #print session_key, 'dropping packet', pkt[TCP].payload
                continue

        if pkt[TCP].flags == 17:  # RST / FIN+ACK
            session_done_cb(sessions[session_key])
            del sessions[session_key]
            #print session_key, 'DONE', is_client_packet, pkt[TCP].flags, pkt[TCP].payload

    for pkts in sessions.values():
        session_done_cb(pkts)


def main(pcap_file):
    pkts = rdpcap(pcap_file)
    assemble_sessions(pkts, print_http)


if __name__ == "__main__":
    main(sys.argv[1])
