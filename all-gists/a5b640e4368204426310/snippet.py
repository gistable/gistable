"""
Requirements:

* A Wordpress Blog
* Ghost export file (json).
* Python Packages: python-wordpress-xmlrpc
  
  >>> pip install python-wordpress-xmlrpc
  
WARNING: 

USE THIS AT YOUR OWN RISK. 
If your have any questions, please comment here below.

"""

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

from dateutil.parser import parse
from time import sleep
import json

xmlrpc_endpoint = ''
username = ''
password = ''

wp = Client(xmlrpc_endpoint, username, password)

filename = 'ghost.export.json'

with open(filename) as f:
    text = f.read()

data = json.loads(text)

for p in data['db'][0]['data']['posts']:
    print p['title']
    
    date = p.get('published_at', None)
    if date is None:
        p.get('created_at')

    post = WordPressPost()
    post.slug = p['slug']
    post.content = p['html']
    post.title = p['title']
    post.post_status = 'publish'
    try:
        post.date = parse(date)
    except:
        continue

    wp.call(NewPost(post))