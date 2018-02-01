import re
import sys
from pygeoip import GeoIP

g = GeoIP('GeoIP.dat')

r = re.compile(r'20. ([0-9]+) "')

d = {}

while True:
    line = sys.stdin.readline()
    if not line: break
    match = r.search(line)
    if match:
        ip = line.split(' ')[0]
        country = g.country_name_by_addr(ip)
        if not country: country = 'Unknown'
        d[country] = int(match.group(1)) + d.get(country, 0)

ds = d.items()
ds.sort(lambda x, y: cmp(y[1], x[1]))
for k, v in ds:
    if v > (1024*1024*1024):
        print k, '%0.2fGb' %(v / (1024*1024*1024.0))