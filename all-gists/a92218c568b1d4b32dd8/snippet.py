import socket, ssl, sys, time
from pprint import pprint as pp
from urlparse import urlparse

if len(sys.argv) != 2:
    print "ERROR: You must supply a url to profile."
    sys.exit(-2)

url = sys.argv[1]

parsed_url = urlparse(url)

s = socket.socket()

if parsed_url.scheme == 'https':
    s = ssl.wrap_socket(s)
    port = 443
elif parsed_url.scheme == 'http':
    port = 80
else:
    print "ERROR: Unsupported scheme. Please enter an http or https URL."
    sys.exit(-1)

url_path = parsed_url.path

if url_path == '':
    url_path = '/'

if parsed_url.query != '':
    url_path += '?'
    url_path += parsed_url.query

CRLF = "\r\n"

request = [
    "GET {} HTTP/1.1".format(url_path),
    "Host: {}".format(parsed_url.netloc),
    "Connection: Close",
    "",
    "",
]

s.connect((parsed_url.netloc, port))
s.send(CRLF.join(request))

headers = []
this_header = ''

start_time = time.time()

byte = s.recv(1)
first_byte = time.time()
print("First byte received in {:.3f}ms.".format((first_byte - start_time) * 1000))

while byte:
    if byte == "\n":
        if this_header == "\r":
            break
        headers.append({
            'time': time.time() - start_time,
            'header': this_header.rstrip()
        })
        this_header = ""
    else:
        this_header += byte
    byte = s.recv(1)

header_end_time = time.time()

for header in headers:
    print("{:9.3f}ms | {}".format(header['time'] * 1000, header['header']))

print("All headers received in {:.3f}ms.".format((header_end_time - start_time) * 1000))

data = s.recv(1024)

while data:
    data = s.recv(1024)

end_time = time.time()
s.close()

print("All data received in {:.3f}ms.".format((end_time - start_time) * 1000))
