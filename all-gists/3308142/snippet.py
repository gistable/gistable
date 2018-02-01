#!/usr/bin/python
# This file should be placed into the /path/to/svn/hooks directory, and should be called by the 
# /path/to/svn/hooks/post-commit bash script. The call should have the full path to the python
# file, and the arguments should be revision and repo (or $1, $2). This will allow you to send
# hooks to your sprint.ly products directly from your SVN client / commit provided that you use
# one of the supported commands from the sprint.ly knowledge base: 
#
# http://support.sprint.ly/kb/integration/available-scmvcs-commands
# 
# Please set the prod variable to your product id, and the hash to the hash in the commit hook 
# url which can be found in your products' management page. i.e. 
# https://sprint.ly/product/1234/commits/zdqansjdk12391bhjek12
# prod = '1234'
# hash = 'zdqansjdk12391bhjek12'
#
# Enjoy! 
import urllib2, urllib, json, sys
import subprocess as sub
from time import gmtime, strftime

# the revision number and repo should be the subverion post-commit arguments $1 and $2 respectively
rev = sys.argv[1]
repo = sys.argv[2]
conf = {"svnlook": "/usr/bin/svnlook"}

# open the svnlook command and retrieve stdout
p = sub.Popen([conf['svnlook'], 'log', '--revision', rev, repo], stdout=sub.PIPE, stderr=sub.PIPE)

svnlook, errors = p.communicate()

message = str(svnlook)
time = strftime("%Y/%m/%d %H:%M:%S", gmtime()) + " +0000"
author = "Your Name" # get this from ssl cert
author_email = "your.email@host.tld" # get this from ssl cert

# other options are available, as per beanstalk documentation
json = json.dumps(
{
    "message": message,
    "time": time,
    "author": author,
    "author_email": author_email,
    "changeset_url": repo,
    "revision": rev,
})

prod = ""
hash = ""

mydata = [('commit',json)]
mydata = urllib.urlencode(mydata)
path = 'https://sprint.ly/product/' + prod + '/commits/' + hash
req = urllib2.Request(path, mydata)
req.add_header("Content-type", "application/json")

# send request
page = urllib2.urlopen(req).read()