# -*- coding: utf-8 -*-
import urllib.request
import re
import datetime
from datetime import timedelta
import ctypes
import winsound

def search(fromDate,toDate):
    found = False
    while not found:
        date = fromDate
        showOneTime = False
        while (date <= toDate):            
            url ='https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate='+date.strftime('%Y-%m-%d')+'&from_station=QYS&to_station=BJP'            
            text = urllib.request.urlopen(url).read().decode('utf-8')
            regular = r'ze_num":"(\d+)'    ##ze_num指的是二等座的数量，其它座类似
            seat_num = re.search(regular,text)
            if seat_num:                
                found = True
                print(date,'有',seat_num.group(1),'票')
                if not showOneTime:
                    showOneTime = True
                    winsound.Beep(2007, 6000)
                    ctypes.windll.user32.MessageBoxW(0, '快去改签！！！！！！！！！！！！！', '有票啦!', 0)
            date = date + timedelta(days=1)                    
                
fromM,fromD,toM,toD = 2,26,3,1
str = '正在查找从%d月%d号到%d月%d号是否有从泉州到北京的票...' %(fromM,fromD,toM,toD)
print(str)
search(datetime.date(2015,fromM,fromD),datetime.date(2015,toM,toD))
input()