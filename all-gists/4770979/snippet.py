send(IP(dst=8.8.8.8) / TCP(dport=53, flags='S', seq=0))
offending_payload = str(DNS(rd=1, qd=DNSQR(qname="dl.dropbox.com")))
offending_payload = struct.pack("!H", len(offending_payload)) + offending_payload
send(IP(dst=8.8.8.8) / TCP(dport=53, flags='A', seq=1, ack=100) / Raw(offending_payload))