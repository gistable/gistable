import time
import boto
from boto.s3.connection import Location

#
# create a couple of strings with our very minimal web content
#
index_html = """
<html>
  <head><title>My S3 Webpage</title></head>
  <body><h2>This is my S3-based website</h2></body>
</html>"""

error_html = """
<html>
  <head><title>Something is wrong</title></head>
  <body><h2>Something is terribly wrong with my S3-based website</h2></body>
</html>"""

# create a connection to S3
conn = boto.connect_s3(host='s3-us-west-1.amazonaws.com')
# create a bucket and make it publicly readable
website_bucket = conn.create_bucket('garnaat-website-2',
                                    location=Location.USWest,
                                    policy='public-read')

# upload our HTML pages and make sure they are publicly readable
# also make sure Content-Type is set to text/html
index_key = website_bucket.new_key('index.html')
index_key.content_type = 'text/html'
index_key.set_contents_from_string(index_html, policy='public-read')
error_key = website_bucket.new_key('error.html')
error_key.content_type = 'text/html'
error_key.set_contents_from_string(error_html, policy='public-read')

# now set the website configuration for our bucket
website_bucket.configure_website('index.html', 'error.html')

time.sleep(5)

# now get the website configuration, just to check it
print website_bucket.get_website_configuration()
