#
# This script scrapes your soldier statistics from Battlelog
# NOTE: This is just a very quick demonstration, it doesn't really do much as-is, besides
#       authenticate to Battlelog and get you a dict of your soldier's statistics. 
#       There is no error handling, no anything. It will only work if everything goes well.
#
#
# Input your Origin username and password into the params dict below and it should work.
#
# In the very bottom, the stats dict will contain the data from the Battlelog JSON response.
# 
# httplib, urllib, sys and json are probably built in to your Python distro
# You may need to install BeautifulSoup manually (eg. easy_install beautifulsoup)
#
import httplib, urllib, sys, json
from BeautifulSoup import BeautifulSoup

battlelog_host = 'battlelog.battlefield.com'
battlelog_baseurl = 'http://battlelog.battlefield.com'

params = urllib.urlencode({
    'email': 'ORIGIN EMAIL ADDRESS',
    'password': 'ORIGIN PASSWORD',
    'submit': 'Sign in',
    'redirect': ''
})

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html'
}

cs = httplib.HTTPSConnection(battlelog_host)
cs.request('POST', '/bf3/gate/login/', params, headers)

r = cs.getresponse()

cs.close()

print r.status, r.reason
print r.getheaders()
print r.read()

print r.getheader('Location')

redirect_url = r.getheader('Location')

if redirect_url != 'http://battlelog.battlefield.com/bf3/':
    sys.exit('Login failure')

sess_cookie = r.getheader('set-cookie').split(';')[0]
sess_headers = {
    'Cookie': sess_cookie
}

home_path = redirect_url.replace(battlelog_baseurl, '')

c = httplib.HTTPConnection(battlelog_host)

c.request('GET', home_path, {}, sess_headers)
r = c.getresponse()

print r.status, r.reason
print r.getheaders()
#http://battlelog.battlefield.com/bf3/soldier/zomgmoz/stats/232812371/

soup = BeautifulSoup(r.read())
stats_path = soup.find('div', id='base-user-statistics').a['href']

soldier_id = stats_path.split('/')[-2]

print 'Loading stats', stats_path, 'for soldier ID', soldier_id
c.request('GET', '/bf3/overviewPopulateStats/%s/bf3-us-assault/1/' % soldier_id, {}, sess_headers)
r = c.getresponse()
print r.status, r.reason
print r.getheaders()

result = json.loads(r.read())
stats = result['data']

c.close()

# access your stats like this:
print stats['overviewStats']['kills']