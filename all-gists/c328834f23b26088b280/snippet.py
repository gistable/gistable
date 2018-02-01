#-*-coding: utf-8 -*-
#!/usr/bin/python
import requests

def sendMsg(msg):
    url_space_login = 'http://f.10086.cn/huc/user/space/login.do?m=submit&fr=space'
    url_login = 'http://f.10086.cn/im/login/cklogin.action'
    url_sendmsg = 'http://f.10086.cn/im/user/sendMsgToMyselfs.action'
    parameter= { 'mobilenum':'yourmobile', 'password':'yourpassword'}

    session = requests.Session()
    session.post(url_space_login, data = parameter)
    session.get(url_login)
    session.post(url_sendmsg, data = {'msg':msg})
    print 'send success !'

if __name__ == '__main__':
    sendMsg('python send fetion')