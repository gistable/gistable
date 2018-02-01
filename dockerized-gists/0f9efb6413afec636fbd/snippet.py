__author__ = 'march'

ips = ["192.312.3", "192.312.3", "192.312.3", "10.10.3.4", "99.23.1.3", "99.23.1.3"]
ts = ["1", "2", "3", "4", "5", "6"]

new_ips = []
new_ts = []

for ip in ips:
    new_ips.append(ip)
    new_ts.append(ts[ips.index(ip)])

    while ips.count(ip) > 1:
        ips.remove(ip)
        del ts[ips.index(ip)]

ips = new_ips
ts = new_ts

print(ips)
print(ts)
