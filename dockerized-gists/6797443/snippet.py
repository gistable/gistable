import urllib2
from cookielib import CookieJar

cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

# login to Piazza.
login_url = 'https://piazza.com/logic/api?method=user.login'
login_data = '{"method":"user.login","params":{"email":"alockwoo@andrew.cmu.edu","pass":"fakePassword"}}'

# if the user/password match, the server respond will contain a session cookie
# that you can use to authenticate future requests.
login_resp = opener.open(login_url, login_data)
print login_resp.read()

# get the content of some random Piazza post on the 15-214 Piazza site.
content_url = 'https://piazza.com/logic/api?method=get.content'
content_data = '{"method":"content.get","params":{"cid":"hm8b1yx8v234m2","nid":"hkqe3rh2nlz35d"}}'
content_resp = opener.open(content_url, content_data)
print content_resp.read()