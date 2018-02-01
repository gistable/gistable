# -*- coding: utf-8 -*-
#当当网图书目录抓取
#已经实现抓取目录
#实现写入到txt文件中
#新增匹配字符串
#新增书名抓取（略有bug）
#作者：Jeffma @ https://gist.github.com/Jeff2Ma/24f6c49877ebbfec9900
#参考 http://blog.csdn.net/nwpulei/article/details/7272832

import urllib2
import re
from sgmllib import SGMLParser
class ListName(SGMLParser):
    def reset(self):
        self.item = []
        self.title = []
        self.flag = False
        self.getdata = False
        self.verbatim = 0
        self.is_h1 = False
        SGMLParser.reset(self)
        
    def start_div(self, attrs):
        if self.flag == True:
            self.verbatim +=1 #进入子层div了，层数加1
            return
        for k,v in attrs:#遍历div的所有属性以及其值
            if k == 'id' and v == 'catalog':
                self.flag = True
                return

    def end_div(self):#遇到</div>
        if self.verbatim == 0:
            self.flag = False
        if self.flag == True:#退出子层div了，层数减1
            self.verbatim -=1

    def start_textarea(self, attrs):
        if self.flag == False:
            return
        self.getdata = True
        
    def end_textarea(self):#遇到</textarea>
        if self.getdata:
            self.getdata = False

    def start_h1(self, attrs):
      self.is_h1 = True

    def end_h1(self):
      self.is_h1 = False

    def handle_data(self, text):#处理文本
        if self.getdata:
            self.item.append(text)
        if self.is_h1:
            self.title.append(text)
            
    def print2txt(self):
        print  '书名：'+self.title[0].decode('gbk').encode('utf8')
    	f = open(filename[0]+'.txt','w')
    	for i in self.item:
            f.write(i.decode('gbk').encode('utf8'))
        f.close()

url = 'http://product.dangdang.com/23422719.html'
number = 'http://product.dangdang.com/(.*).html'
filename = re.findall(number,url)
# print filename[0]
content =urllib2.urlopen(url).read()
print ('正在读取'+url+'的内容...')
lister = ListName()
lister.feed(content)
lister.print2txt()
print('目录已抓取写入到'+filename[0]+'.txt中,end~')