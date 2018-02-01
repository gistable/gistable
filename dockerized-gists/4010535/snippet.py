##
## PG&E Green button data downloader
##
## @author Stephen Dawson-Haggerty <stevedh@eecs.berkeley.edu>
## 
## Based on https://gist.github.com/3131346 and Andrew Krioukov's
## sMAPv1 PG&E driver for the old format of data.
## 

import os
import errno
import re
import mechanize
import zipfile
import tempfile
from cStringIO import StringIO

user = 'username'
passwd = 'password'
outdir = "pge-data"
agent = "User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3"

def select_form(forms, name):
  form = None
  for f in forms:
    if f.name == name:
      if form != None:
        raise ValueError("Error: multiple forms found with name = " + name)
      form = f

  if form == None:
    raise ValueError("Error: no forms found with name = " + name)

  return form

try:
    # make the output directory first so we know if we can access it
    os.makedirs(outdir)
except os.error, e:
    if e.errno != errno.EEXIST:
        raise

br = mechanize.Browser()
# not sure if these are all still necessary
br.set_debug_http(False)
br.set_handle_equiv(False) # Otherwise, the loading page goes into an inf loop
br.set_handle_robots(False)
br.set_handle_referer(False)
br.set_handle_refresh(False)

def request(req):
    req.add_header("User-Agent", agent) 
    return br.open(req)

print "Get login page"
request(mechanize.Request("https://www.pge.com/myenergyweb/appmanager/pge/customer"))

print "Logging in"
f = select_form(br.forms(), 'login')
f['USER'] = user
f['PASSWORD'] = passwd
request(f.click())

print "Continue to opower"
request(br.click_link(text="My Usage"))

print "Continue pg&e-side sso"
f = br.forms().next()           # get the first form
request(f.click())

print "Continue the opower sso"
f = br.forms().next()
request(f.click())

print "Downloading all data"
request(br.click_link(url_regex=re.compile(".*export-dialog$")))

f = br.forms().next()
f.find_control("exportFormat").items[-1].selected = True
f['from'] = "04/11/2012"
f['to'] = "05/11/2012"
resp = request(f.click())

# make a zipfile
data = zipfile.ZipFile(StringIO(resp.read()))
# and extract the contents
for name in data.namelist():
    if name.endswith("/"): continue
    print "extracting", name
    with open(os.path.join(outdir, name), 'wb') as fp:
        fp.write(data.read(name))
