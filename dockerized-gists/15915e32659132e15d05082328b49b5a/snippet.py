#-*- coding=utf-8 -*-
import requests
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')


signin='http://v2ex.com/signin'
home='http://v2ex.com'
url='http://v2ex.com/mission/daily'
headers = {  
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',  
    'Origin': 'http://www.v2ex.com',  
    'Referer': 'http://www.v2ex.com/signin',  
    'Host': 'www.v2ex.com',  
}
data={}

def sign(username,passwd):
    try:
        session=requests.Session()
        session.headers=headers
        loginhtm=session.get(signin).content
        usernameform=re.findall('<input type="text" class="sl" name="(.*?)"',loginhtm)[0]
        passwdform=re.findall('<input type="password" class="sl" name="(.*?)"',loginhtm)[0]
        onceform=re.findall('<input type="hidden" value="(.*?)" name="once" />',loginhtm)[0]
        print usernameform
        print passwdform
        print onceform
        data[usernameform]=username
        data[passwdform]=passwd
        data['once']=onceform
        data['next']='/'
        loginp=session.post(signin,data=data)
        sign=session.get(url).content
        qiandao=re.findall("location.href = '(.*?)'",sign)[0]
        session.get(home+qiandao)
        print u'签到成功'
    except Exception,e:
        print e



if __name__=='__main__':
    #username,passwd更改为你自己的用户名、密码
    username=''
    passwd=''
    requests.packages.urllib3.disable_warnings()
    sign(username,passwd)