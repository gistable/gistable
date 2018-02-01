import urllib2
import zipfile
import StringIO

response = urllib2.urlopen('http://some_url.zip')
body = response.read()
io = StringIO.StringIO(body)
# io is a file-like object... you can use it where you'd use a file!
myfile = zipfile.ZipFile(io)
