#!/usr/bin/python

# Simple python script that takes a html file extracts all scripts and concatenates them into
# a single file. The concatenated script is then sent to the google closure compiler for further
# squishing.
# Finally a game.zip archive is created with all specified files. The size of this archive
# is printed to standard output
#
# Usage: 
# In the terminal type:
# python min.py OR ./min.py (providing it is executable and python is in your $PATH)

from BeautifulSoup import BeautifulSoup, Tag
from zipfile import ZipFile, ZIP_DEFLATED
import os, httplib, urllib, sys, shutil 

# name of our dev html file. we'll pull all js files out of here
dev = 'dev.html'
index = 'index.html'
# closure compiler method. options SIMPLE, ADVANCED and WHITESPACE_ONLY 
optimise = 'SIMPLE'
# destination for our concatented and compressed js file 
compressed = 'g.js'
# files to be included in the zip
files = ['index.html', 'b.gif', 'favicon.ico', compressed]
# target folder for all our zip files
folder = 'game'

# grab all scripts from our dev html for concatentation 
dev_file = open(dev, 'r')
html = dev_file.read()
dev_file.close()
soup = BeautifulSoup(html)
concat_js = open('all.js', 'w')

scripts = soup.findAll(['script'])
for script in scripts:
    if script.has_key('src'):
        src = open(script['src'], 'r')
        concat_js.write(src.read())
        src.close()
concat_js.close()


# get contat'd js to send to the closure compiler
js = open('all.js').read()
params = urllib.urlencode([
    ('js_code', js),
    ('compilation_level', optimise + '_OPTIMIZATIONS'),
    ('output_format', 'text'),
    ('output_info', 'compiled_code'),
  ])

headers = { "Content-type": "application/x-www-form-urlencoded" }
conn = httplib.HTTPConnection('closure-compiler.appspot.com')
conn.request('POST', '/compile', params, headers)
response = conn.getresponse()
data = response.read()
conn.close


# and write the closure output to our js file
final_js = open(compressed, 'w')
final_js.write(data);
final_js.close()


# update our index.html to mirror dev.html
dev_file = open(dev, 'r')
html = dev_file.read() 
dev_file.close()

soup = BeautifulSoup(html)

# remove all script tags
for tag in soup.findAll('script'):
    tag.extract()

# append final script tag to body
script = Tag(soup, "script")
script["src"] = compressed
soup.body.insert(soup.body.contents, script)

index_file = open(index, 'w')
index_file.write(soup.prettify())
index_file.close()


# create folder for our game, if it doesnt exist
if not os.path.exists(folder):
    os.makedirs(folder)

# copy files into folder (to avoid creating a zip bomb)
for filename in files:
    shutil.copy2(filename, folder + '/' + filename)


# zip all our files
zf = ZipFile(folder + '.zip', 'w', ZIP_DEFLATED)
for filename in files:
    zf.write(folder + '/' + filename)
zf.close()

# and a bit of a cleanup
shutil.rmtree(folder)

# finally, tell us how much we've squeezed in
total = os.path.getsize(folder + '.zip')
remaining = 13312 - total
print 'Total used: ', total
print 'Bytes remaining: ', remaining

