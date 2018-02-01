#encoding=utf-8
import requests
from bs4 import BeautifulSoup
import re
import sys
import datetime


uid="11111"   #用户名
pwd="11111"   #密码


http = requests.Session()
http.headers.update({
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    ,'Accept-Language':"zh-CN,zh;q=0.8,ko;q=0.6,zh-TW;q=0.4"
})
#http.proxies = {"http":"http://127.0.0.1:8080","https":"http://127.0.0.1:8080"}

##打开登陆界面
res=http.get("http://www.hostloc.com/member.php?mod=logging&action=login&infloat=yes&handlekey=login&inajax=1&ajaxtarget=fwin_content_login")
match=re.search(r'name="formhash" value="(\S+)"',res.text)
if(match):
    formhash=match.group(1)
else:
    exit(0)
    
##登陆
form={
    "formhash":formhash
    ,"referer":"http://www.hostloc.com/thread-12949-1-1.html"
    ,"loginfield":"username"
    ,"username":uid
    ,"password":pwd
    ,"questionid":0
    ,"answer":""
    ,"loginsubmit":"true"
}
res=http.post("http://www.hostloc.com/member.php?mod=logging&action=login&loginsubmit=yes&handlekey=login&loginhash=LWKbr&inajax=1",data=form)
match=re.search(r"'uid':'",res.text)
if(match):
    print("登陆成功")
else:
    print("登陆失败")
    exit(0)
##查询今天访问的空间数量  
res=http.get("http://www.hostloc.com/home.php?mod=spacecp&ac=credit&op=log&suboperation=creditrulelog")
bs=BeautifulSoup(res.text,"html.parser")
td=bs.find('td',string="访问别人空间")
if(td==None): 
    print("信息获取失败")
    exit(0)
tds=td.parent.find_all("td")
today_view_count=int(tds[2].text)    #今天已经翻牌数
last_view_date=tds[5].text         #上次翻牌时间，这个时间不会自动刷新，所以不能仅仅依据数量就决定不翻牌
need_view=last_view_date.find(datetime.datetime.now().strftime("%Y-%m-%d"))==-1    #上次翻牌时间是不是今天，不是今天则需要翻
if(today_view_count>=10 and (not need_view)):       #不论数量多少，只要上次翻牌时间不是今天就翻。上次翻牌是今天才去判断数量
    print("今日累了，明日再翻！")
    exit(0)
##去首页获取等待临幸的网址
res=http.get("http://www.hostloc.com/forum-45-1.html")
users   =re.findall("(space-uid\S+)\"",res.text)
viewed=set()
num=0
while num <13:
    url = users.pop()
    if(url in viewed):continue
    viewed.add(url)
    print(url)
    res=http.get('http://www.hostloc.com/'+url)
    users.extend(re.findall("(space-uid\S+)\"",res.text))
    num+=1
   
print("今日累了，明日再翻！")