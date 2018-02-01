country = 'fr'
device = "Nokia N95 8Gb"
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
mmap_url = 'http://www.google.com/glm/mmap'
geo_url = 'http://maps.google.com/maps/geo'
 
from struct import pack, unpack
from httplib import HTTP
import urllib2
 
def fetch_latlong_http(query):
    http = HTTP('www.google.com', 80)
    http.putrequest('POST', '/glm/mmap')
    http.putheader('Content-Type', 'application/binary')
    http.putheader('Content-Length', str(len(query)))
    http.endheaders()
    http.send(query)
    code, msg, headers = http.getreply()
    result = http.file.read()
    return result
 
def fetch_latlong_urllib(query):
    headers = { 'User-Agent' : user_agent }
    req = urllib2.Request(mmap_url, query, headers)
    resp = urllib2.urlopen(req)
    response = resp.read()
    return response
 
fetch_latlong = fetch_latlong_http
 
def get_location_by_cell(cid, lac, mnc=0, mcc=0, country='fr'):
    b_string = pack('&gt;hqh2sh13sh5sh3sBiiihiiiiii',
                    21, 0,
                    len(country), country,
                    len(device), device,
                    len('1.3.1'), "1.3.1",
                    len('Web'), "Web",
                    27, 0, 0,
                    3, 0, cid, lac,
                    0, 0, 0, 0)
 
    bytes = fetch_latlong(b_string)
    (a, b,errorCode, latitude, longitude, c, d, e) = unpack("&gt;hBiiiiih",bytes)
    latitude = latitude / 1000000.0
    longitude = longitude / 1000000.0
 
    return latitude, longitude
 
def get_location_by_geo(latitude, longitude):
    url = '%s?q=%s,%s&amp;output=json&amp;oe=utf8' % (geo_url, str(latitude), str(longitude))
    return urllib2.urlopen(url).read()
 
if __name__ == '__main__':
    print i,get_location_by_cell(20465, 495, 3, 262)
    print get_location_by_cell(20442, 6015)
    print get_location_by_cell(1085, 24040)
    print get_location_by_geo(40.714224, -73.961452)
    print get_location_by_geo(13.749113, 100.565327)