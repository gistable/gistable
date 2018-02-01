1.  首先验证 web server 支持断点续传:

(django13)[www@mail ~]$ curl -i http://127.0.0.1/123.txt
HTTP/1.1 200 OK
Server: nginx/0.8.54
Date: Tue, 26 Jul 2011 14:41:53 GMT
Content-Type: text/plain
Content-Length: 10
Last-Modified: Tue, 26 Jul 2011 14:32:35 GMT
Connection: keep-alive
Accept-Ranges: bytes

123456789

2.  然后按照 rfc2616 传送对应的 header:

(django13)[www@mail ~]$ python
Python 2.7.1 (r271:86832, May 19 2011, 13:05:13)
[GCC 4.1.2 20080704 (Red Hat 4.1.2-50)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import httplib2
>>> h = httplib2.Http()
>>> h.request('http://127.0.0.1/123.txt', headers={'Range': 'bytes=0-4'})
({'status': '206', 'content-length': '5', 'content-range': 'bytes 0-4/10', 'server': 'nginx/0.8.54', 'last-modified': 'Tue, 26 Jul 2011 14:32:35 GMT', 'connection': 'keep-alive', 'date': 'Tue, 26 Jul 2011 14:43:19 GMT', 'content-type': 'text/plain'}, '12345')
>>> h.request('http://127.0.0.1/123.txt', headers={'Range': 'bytes=4-'})
({'status': '206', 'content-length': '6', 'content-range': 'bytes 4-9/10', 'server': 'nginx/0.8.54', 'last-modified': 'Tue, 26 Jul 2011 14:32:35 GMT', 'connection': 'keep-alive', 'date': 'Tue, 26 Jul 2011 14:43:38 GMT', 'content-type': 'text/plain'}, '56789\n')
