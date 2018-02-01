# -*- coding: utf-8 -*-
import requests
import hashlib
import re

username = '' ###账号###
password =  ''###密码###
UA = "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/27.0.1453.116 Safari/537.36"
headers = {
            "User-Agent": UA,
            "Host": "bbs.hshy.net"
            }

class hshy(object):
    def __init__(self,
                 username,
                 password,
                 number = None,
                 login_url = 'http://bbs.hshy.net/member.php',
                 checkin_url = 'http://bbs.hshy.net/plugin.php'):
        self.username = username.decode('UTF-8').encode('GBK')
        self.password = hashlib.md5(password).hexdigest()
        self.number = number
        self.login_url = login_url
        self.checkin_url = checkin_url
        self.hshy_session = requests.Session()

    def try_login(self):
        rqs = self.hshy_session.get(self.login_url,params = {"referer":'',
                                        "mod":	"logging",
                                        "action":"login"},headers = headers).text
        loginhash = re.search(r'<div id="main_messaqge_(.+?)">',rqs).group(1).encode('ascii')
        formhash = re.search(r'<input type="hidden" name="formhash" value="(.+?)" />',rqs).group(1).encode('ascii')
        post_data = {'answer':'',
                        'formhash':formhash,
                        'loginfield':'username',
                        'password':self.password,
                        'questionid':0,
                        'referer':'http://bbs.hshy.net/./',
                        'username':self.username}
        postrqs = self.hshy_session.post(self.login_url,params = {'mod':'logging',
                                                'action':'login',
                                                'loginsubmit':'yes',
                                                'loginhash':loginhash,
                                                'inajax':1},data = post_data,headers = headers)
        if re.search(u'现在将转入登录前页面',postrqs.text):
            return 'login successful'
        else:
            self.notify()
            exit()

    #获取打卡post的formhash参数
    def checkinformhash(self):
        checkinformhash = self.hshy_session.get(self.checkin_url,params = {'id':	"dsu_amupper:ppering",
                                                    "infloat":	"yes",
                                                    "handlekey":"pper",
                                                    "referer":	"http://bbs.hshy.net/",
                                                    "inajax":	1,
                                                    "ajaxtarget":	"fwin_content_pper"},headers = headers).text
        return re.search(r'pper&ppersubmit=true&formhash=(.+?)\'',checkinformhash).group(1).encode('ascii')

    #失败发送短信提醒
    def notify(self):
        """
        使用nexmo发送提醒短信，如若使用需注册nexmo服务,将得到key和secret以调用其API~~
        """
        if self.number:
            key = ''  ###你的Key
            secret = ''  ###你的Secret
            data = {'api_key': key,
                'api_secret': secret,
                'from': 'anywhere',
                'to': self.number,
                'type': 'unicode',
                'text': u'登陆或领取失败，请手动领取'
                    }
            rps = requests.post('https://rest.nexmo.com/sms/json',data = data)
            return rps.text
        else:
            pass

    def checkin(self):
        self.try_login()
        params = {  'id':'dsu_amupper:pper',
                    'ppersubmit':'true',
                    'formhash':self.checkinformhash(),
                    'infloat':'yes',
                    'handlekey'	:'dsu_amupper',
                    'referer':	'http://bbs.hshy.net/',
                    'inajax':1,
                    'ajaxtarget':	'fwin_content_dsu_amupper'}
        checkin = self.hshy_session.get(self.checkin_url,params = params ,headers = headers)
        if re.search(u'恭喜',checkin.text):
            print u'checkin successful'
        else:
            print u'checkin failed'
            self.notify()

if __name__ == '__main__':
    hshy(username,password).checkin()