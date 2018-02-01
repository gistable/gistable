import urlparse
import httplib
import base64

proxy_uri = "http://user:password@proxy_host:proxy_port"
host = 'www.google.com'
port = 443

url = urlparse.urlparse(proxy_uri)
conn = httplib.HTTPSConnection(url.hostname, url.port)
headers = {}
if url.username and url.password:
    auth = '%s:%s' % (url.username, url.password)
    headers['Proxy-Authorization'] = 'Basic ' + base64.b64encode(auth)

conn.set_tunnel(host, port, headers)
conn.request("GET", "/")
response = conn.getresponse()
print response.status, response.reason
output = response.read()