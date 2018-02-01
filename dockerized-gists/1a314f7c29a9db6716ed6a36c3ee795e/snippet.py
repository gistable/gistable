import re
import httplib
import urllib, urllib2, cookielib

def solve(n):
	sum = 0
	i = 0
	num = 2
	while i < n:
		f = 0
		for j in xrange(2, num):
			if(num % j) == 0:
				f = 1
				break
		if f == 0:
			#print num
			sum = sum + num
			i = i + 1
		num = num + 1
	return sum

conn = httplib.HTTPConnection("hack.bckdr.in")
res = conn.request("GET", 'http://hack.bckdr.in/2013-MISC-75/misc75.php')
res = conn.getresponse()
txt = res.read()
nn = [int(c) for c in txt.split() if c.isdigit()]
N = nn[1]
sum = solve(N)

headers = res.getheaders()
cookies = headers[2][1]

headers = {"Content-type": "application/x-www-form-urlencoded"
			, "Cookie": cookies
			, "Host": "hack.bckdr.in"
			, "Connection" : "keep-alive"
			, "Cache-Control" : "max-age=0"
			, "Origin": "http://hack.bckdr.in"
			, "Referer": "http://hack.bckdr.in/2013-MISC-75/misc75.php"
			, "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36"}

params = urllib.urlencode({'answer': sum, 'submit': 'Submit'})
res = conn.request("POST", 'http://hack.bckdr.in/2013-MISC-75/misc75.php', params, headers)
res = conn.getresponse()
print res.read()