# Fetches an url and scan the html document for a regex pattern (the STEAM KEY)
# monitoring if the KEY changes and copying it to the system's clipboard. 
#
# Output:
# CBT2J-R0GID-8FAJI -> 12:20
# K5RJH-86RH7-W0Y2W -> 12:25
# IV37H-83VGQ-MT9BF -> 12:30
# WY2T9-Q35ZV-8LYCX -> 12:35
# MR7BH-RJ3VJ-MADHW -> 12:40
# HBQPD-BFCG7-06577 -> 12:45
# 39PJE-GC8V4-DLFDQ -> 12:50
# Z86PY-THHHR-RMCBG -> 12:55


import re, time, urllib2
# cross-platform copy-to-clipboard 
# http://coffeeghost.net/2010/10/09/pyperclip-a-cross-platform-clipboard-module-for-python/
# drop it inside your C:\Python27\Lib on Windows.
import pyperclip 

last_code = ''
while True:
    f = urllib2.urlopen('http://www.exosyphen.com/page_10years.html')
    p = f.readlines()
    for i in p:
        if "Newest" in i:
            code = re.findall(r'[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+', i)[0]            
            if code != last_code:
                print code+' -> '+time.strftime("%H:%M" ,time.localtime( time.time()))
                pyperclip.copy(code)
                last_code = code                
            break

    time.sleep(5)