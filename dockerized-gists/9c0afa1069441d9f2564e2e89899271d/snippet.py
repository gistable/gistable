# coding=utf-8                                                                                                                                    
# pip install zhihu_oauth                                                                                                                         
                                                                                                                                                  
import os                                                                                                                                         
import time                                                                                                                                       
import json                                                                                                                                       
                                                                                                                                                  
from zhihu_oauth import ZhihuClient                                                                                                               
                                                                                                                                                  
TOKEN_FILE = 'token.pkl' 
API = 'https://www.zhihu.com/api/v4/messages'

client = ZhihuClient()                                                                                                                                                                                                                                                           
                                                                                                                                                  
if os.path.isfile(TOKEN_FILE):                                                                                                                    
    client.load_token(TOKEN_FILE)                                                                                                                 
else:                                                                                                                                             
    client.login_in_terminal()                                                                                                                    
    client.save_token(TOKEN_FILE)     
    
me = client.me()
                                                                                                                                                  
rs = list(me.lives)                                                                                                                               
live = rs[0]                                                                                                                                      
if int(live.id) != 827530183664861184:                                                                                                            
    raise TypeError()                                                                                                                             

content = '''
抱歉打扰，你参加的Live「爬虫从入门到进阶」中丢了5个录音（知乎技术问题造成），我已经在4月15日晚上把他们补在了最后，请注意收听！
 
-  一个小爬虫'''
                                                                                                                                                  
for p in live.participants:                                                                                                                       
    r = me._session.post(API, data=json.dumps({                                                                                                   
        'type': "common", 'content': content, 'receiver_hash': p[2].id}))                                                                         
    if r.status_code == 403 and '对方没有关注你' not in r.json()['error']['message']:                                                             
        break                                                                                                                                     
    time.sleep(10)                 