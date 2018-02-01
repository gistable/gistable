#coding=utf8
 
##版本：1.0
##环境：python2.7
##作者：moxie
##日期：2013.08.23
##说明：文件生成目录为：D:/ludatui

import urllib2,urllib
import re
import threading
import os
import sys
import datetime

pages = 1 #要下载的页数
today = datetime.date.today().isoformat()

s = os.sep
root = "d:" + s + "ludatui" + s
if False == os.path.exists(root):
    os.mkdir(root)

prefix = 'http://loudatui.com/?page='
replace = 'large'
pat = r'<img alt="Small" class="img" src="(.*?)small" />'
pattern = re.compile(pat)



def dlitem(url,i,k):
    fname = today + '-' + str(i)+'-' + str(k+1) + '.jpg'
    urllib.urlretrieve(url,os.path.join(root,fname))
 
def dlpage(i):
    page = urllib2.urlopen(prefix + str(i)).read()
    items = pattern.findall(page)
    targets = [item + replace for item in items]
    tasks = []
    for k in range(len(targets)):
        try:
            t = threading.Thread(target=dlitem,args=(targets[k],i,k))
            tasks.append(t)
        except:
            print 'some error in %sth download' % k
            continue
    for task in tasks:
        task.start()
     
    for task in tasks:
        task.join(300)
    return 0


for n in range(pages):
    print 'Now page %s' % str(n+1)
    dlpage(n+1)
    print 'Page %s OK\n' % str(n+1)

#print '\n%s pics downloaded!' % str(count-1)

