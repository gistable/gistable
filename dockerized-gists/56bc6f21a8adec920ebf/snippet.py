import gzip
import json
import requests
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

# Let's fetch the Common Crawl FAQ using the CC index
resp = requests.get('http://index.commoncrawl.org/CC-MAIN-2015-27-index?url=http%3A%2F%2Fcommoncrawl.org%2Ffaqs%2F&output=json')
pages = [json.loads(x) for x in resp.content.strip().split('\n')]
# Multiple pages may have been found - we're only interested in one
page = pages[0]

# If we print this, we'll see the JSON representation of the response
# Most important is the file path to read and the location within the large file that the GZIP response exists
print 'JSON response from index.commoncrawl.org'
print '---'
print page
print '---'

# We need to calculate the start and the end of the relevant byte range
# (each WARC file is composed of many small GZIP files stuck together)
offset, length = int(page['offset']), int(page['length'])
offset_end = offset + length - 1
# We'll get the file via HTTPS so we don't need to worry about S3 credentials
# Getting the file on S3 is equivalent however - you can request a Range
prefix = 'https://aws-publicdatasets.s3.amazonaws.com/'
# We can then use the Range header to ask for just this set of bytes
resp = requests.get(prefix + page['filename'], headers={'Range': 'bytes={}-{}'.format(offset, offset_end)})

# The page is stored compressed (gzip) to save space
# We can extract it using the GZIP library
raw_data = StringIO(resp.content)
f = gzip.GzipFile(fileobj=raw_data)

# What we have now is just the WARC response, formatted:
data = f.read()
warc, header, response = data.strip().split('\r\n\r\n', 2)
#
print 'WARC headers'
print '---'
print warc[:100]
print '---'
print 'HTTP headers'
print '---'
print header[:100]
print '---'
print 'HTTP response'
print '---'
print response[:100]