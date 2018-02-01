#!/usr/bin/python

'''
	InFB - Information Facebook
	Usage: infb.py user@domain.tld password
	http://ruel.me
	
	Copyright (c) 2011, Ruel Pagayon
	All rights reserved.

	Redistribution and use in source and binary forms, with or without
	modification, are permitted provided that the following conditions are met:
		* Redistributions of source code must retain the above copyright
		  notice, this list of conditions and the following disclaimer.
		* Redistributions in binary form must reproduce the above copyright
		  notice, this list of conditions and the following disclaimer in the
		  documentation and/or other materials provided with the distribution.
		* Neither the name of the author nor the names of its contributors 
		  may be used to endorse or promote products derived from this software 
		  without specific prior written permission.

	THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND ANY 
	EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
	WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
	DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, 
	INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
	LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, 
	OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
	LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
	OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
	ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import sys
import re
import urllib
import urllib2
import cookielib
import csv
import json

def main():
	# Check the arguments
	if len(sys.argv) != 3:
		usage()
	user = sys.argv[1]
	passw = sys.argv[2]
	
	# Initialize the needed modules
	CHandler = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
	browser = urllib2.build_opener(CHandler)
	browser.addheaders = [('User-agent', 'InFB - ruel@ruel.me - http://ruel.me')]
	urllib2.install_opener(browser)
	
	
	# Initialize the cookies and get the post_form_data
	print 'Initializing..'
	res = browser.open('http://m.facebook.com/index.php')
	mxt = re.search('name="post_form_id" value="(\w+)"', res.read())
	pfi = mxt.group(1)
	print 'Using PFI: %s' % pfi
	res.close()
	
	# Initialize the POST data
	data = urllib.urlencode({
		'lsd'				: '',
		'post_form_id'		: pfi,
		'charset_test' 		: urllib.unquote_plus('%E2%82%AC%2C%C2%B4%2C%E2%82%AC%2C%C2%B4%2C%E6%B0%B4%2C%D0%94%2C%D0%84'),
		'email'				: user,
		'pass'				: passw,
		'login'				: 'Login'
	})
	
	# Login to Facebook
	print 'Logging in to account ' + user
	res = browser.open('https://www.facebook.com/login.php?m=m&refsrc=http%3A%2F%2Fm.facebook.com%2Findex.php&refid=8', data)
	rcode = res.code
	if not re.search('Logout', res.read()):
		print 'Login Failed'
		
		# For Debugging (when failed login)
		fh = open('debug.html', 'w')
		fh.write(res.read())
		fh.close
		
		# Exit the execution :(
		exit(2)
	res.close()
	
	# Get Access Token
	res = browser.open('http://developers.facebook.com/docs/reference/api')
	conft = res.read()
	mat = re.search('access_token=(.*?)"', conft)
	acct = mat.group(1)
	print 'Using access token: %s' % acct
	
	# Get friend's ID
	res = browser.open('https://graph.facebook.com/me/friends?access_token=%s' % acct)
	fres = res.read()
	jdata = json.loads(fres)
	
	# Initialize the CSV writer
	fbwriter = csv.writer(open('%s.csv' % user, 'ab'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	
	# God for each ID in the JSON response
	for acc in jdata['data']:
		fid = acc['id']
		fname = acc['name']
		
		# Go to ID's profile
		res = browser.open('http://m.facebook.com/profile.php?id=%s&v=info&refid=17' % fid)
		xma = re.search('mailto:(.*?)"', res.read())
		if xma:
			
			# Replace the html entity from the scraped information
			email = xma.group(1).replace('&#64;', '@')
			
			# In case there will be weird characters, repr() will help us.
			try:
				print fname, email
			except:
				print repr(fname), repr(email)
				
			# Write to CSV, again with repr() if something weird prints out.
			try:
				fbwriter.writerow([fname, email])
			except:
				fbwriter.writerow([repr(fname), repr(email)])
	
	
def usage():
	'''
		Usage: infb.py user@domain.tld password
	'''
	print 'Usage: ' + sys.argv[0] + ' user@domain.tld password'
	sys.exit(1)
	
if __name__ == '__main__':
	main()