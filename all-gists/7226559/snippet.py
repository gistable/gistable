# coding= utf-8
from bs4 import BeautifulSoup
from ConfigParser import ConfigParser
from PySide.QtCore import QThread,Qt,Signal
from PySide.QtGui import QTableWidget,QAbstractItemView,QTableWidgetItem,QBrush,QColor,QApplication
from threading import Thread
import webbrowser
import sys
import time
#from urllib2 import urlopen

import urllib
import urllib2

CONFIGFILE='videoupdater.txt'
SECTION='lastest'

opener=urllib2.build_opener(urllib2.HTTPCookieProcessor())
opener.addheaders=[('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0'),
                   ('Content-Type', 'application/x-www-form-urlencoded')]
                   
VIDEO=[(u'我真的是专家','http://i.youku.com/u/UNDE0MTc5OTI=/videos','UNDE0MTc5OTI','youku'),
       (u'sinbasara','http://i.youku.com/u/UMzQ5MjA4NDI4/videos','UMzQ5MjA4NDI4','youku'),
       (u'123来呀','http://i.youku.com/u/UMzEwNTUzNjc2/videos','UMzEwNTUzNjc2','youku'),
       (u'飞碟说','http://i.youku.com/u/UNTMxOTkwNjA0/videos','UNTMxOTkwNjA0','youku'),
       (u'笑打扮哲学','http://i.youku.com/u/UMTM4NDk2MjA=/videos','UMTM4NDk2MjA','youku'),
       (u'各种被干','http://i.youku.com/u/UMTQ0NzE0NzI0/videos','UMTQ0NzE0NzI0','youku'),
       (u'敖厂长y','http://i.youku.com/u/UMjA0NTg4Njcy/videos','UMjA0NTg4Njcy','youku'),
       (u'hawkao','http://i.youku.com/u/UMjU1MzY1ODg=/videos','UMjU1MzY1ODg','youku'),
       (u'财经郎眼','http://www.youku.com/show_page/id_zc0818720404711e29013.html','id_zc0818720404711e29013','youkushow'),
       (u'天天向上','http://www.youku.com/show_page/id_z9510781e2d4411e296ac.html','id_z9510781e2d4411e296ac','youkushow'),
       (u'快乐大本营','http://www.youku.com/show_page/id_zd18a7caa2d4311e29498.html','id_zd18a7caa2d4311e29498','youkushow'),
       #(u'老友记','http://www.youku.com/show_page/id_zafef34ece06211e19013.html','id_zafef34ece06211e19013','youkushow'),
       (u'晓说','http://www.youku.com/show_page/id_z64feb2249b8211e296da.html','id_z64feb2249b8211e296da','youkushow'),
       #(u'娱乐百分百','http://www.youku.com/show_page/id_z8fad81de2d6011e296ac.html','id_z8fad81de2d6011e296ac','youkushow'),
       (u'国光帮帮忙','http://www.youku.com/show_page/id_z5ca3d0742d4f11e2b356.html','id_z5ca3d0742d4f11e2b356','youkushow'),
       (u'罗辑思维','http://www.youku.com/show_page/id_zc40101545bdc11e2b356.html','id_zc40101545bdc11e2b356','youkushow'),
       #(u'十万个冷笑话','http://www.youku.com/show_page/id_z02baa1f0cbcf11e19013.html','id_z02baa1f0cbcf11e19013','youkushow_r'),
       (u'壹读','http://i.youku.com/u/UNDY0MTExNTky/videos','UNDY0MTExNTky','youku'),
       (u'lukePOST','http://i.youku.com/u/UMzA3NzkwMzI4/videos','UMzA3NzkwMzI4','youku'),
       
       (u'敖厂长t','http://www.tudou.com/home/item_u29083386s0p1.html','item_u29083386s0p1','tudou'),
       (u'老湿alwayswet','http://www.tudou.com/home/item_u60173626s0p1.html','item_u60173626s0p1','tudou'),
       
       (u'微播江湖','http://video.56.com/opera/6268.html','opera6268','56'),
       (u'反犬TDog','http://i.56.com/fanquan/videos/','fanquan','56i'),

       (u'锵锵三人行','http://phtv.ifeng.com/program/qqsrx/','qiangqiangsanrenxing','ifeng'),

       (u'康熙来了','http://v.qq.com/variety/column/column_324.html','kangxilaile','qq'),
       (u'新闻百科','http://v.qq.com/cover/b/bfal45ox1erftku.html','bfal45ox1erftku','qq2')]
result=[]

class Checker(Thread):
    def __init__(self,user,url,id_,type_):
        Thread.__init__(self)
        self.user=user
        self.url=url
        self.id_=id_
        self.type=type_
        
    def soup(self):
        #return BeautifulSoup(urlopen(self.url))
        return BeautifulSoup(opener.open(urllib2.Request(self.url)).read())
    
    def update(self):
        global config
        print self.url
        timeaskey = False
        if self.type=='youku':
            info = self.soup().find("ul", class_="v")
            self.title = info.a.get('title')
            self.link = info.a.get('href')
            self.time = info.find('li', class_="v_pub").span.string

        elif self.type=='tudou':
            info = self.soup().find("div", class_="txt")
            self.link = info.a.get('href')
            self.title = info.a.get('title')
            self.time = info.find_all('li',limit=2)[1].string[9:].strip()
            
        elif self.type=='56':
            info = self.soup().find("div", class_="episode_cnt").find('a')
            self.link=info.get('href')
            self.title=info.find("span",class_="txt").string
            self.time=info.find("span",class_="time").string
            
        elif self.type=='youkushow':
            info = self.soup().find("div", id="episode").find('li')
            self.link = info.a.get('href')
            self.title = info.a.get('title')
            self.time=info.label.string
        
        elif self.type=='qq':
            info = self.soup().find("div", class_="mod_item")
            temp = info.find('h6').a
            self.title = temp.get('title')+(','.join([a.string for a in info.find('li', class_='date').find_all('a')]))
            self.link = temp.get('href')
            #self.time = info.find('span', class_="mod_version").string[5:10]
            self.time = info.find('em', class_="mask_txt").string[5:10]
            
        elif self.type=='ifeng':
            info = self.soup().find("h2")
            self.title = info.span.string
            self.link = self.url
            self.time = info.em.string[5:10]
            timeaskey = True
            
        elif self.type=='youkushow_r':
            info = self.soup().find("div", id="episode").find_all('a')[-1]
            self.link = info.get('href')
            self.title = info.get('title')
            self.time = self.title[0:2]
            self.title = self.title[2:].strip()
            
        elif self.type=='qq2':
            info = self.soup().find('li',class_='item')
            self.title = info.find('strong',class_='video_title').string
            self.link = self.url
            self.time = info.a.get('ut')[5:]
            timeaskey = True
        
        elif self.type=='56i':
            info = self.soup().find("div", class_="m_v_list_txt")
            tmp = info.find('a')
            self.link=tmp.get('href')
            self.title=tmp.get('title')
            self.time=info.find('span').string[3:]
        
        if timeaskey:
            self.key=self.time
        else:
            self.key=self.link
            
        new=False
        if not config.has_option(SECTION, self.id_) or not config.get(SECTION, self.id_)==self.key:
            config.set(SECTION, self.id_, self.key)
            new=True
        result.append((self.user,self.time,self.title,self.link,new))
        
    def run(self):
#        self.update()
         try:
             self.update()
         except:
             print 'error'
             result.append((self.user,'error','error',self.url,True))
        
class Updater(object):
    def __init__(self):
        global config
        config = ConfigParser()
        config.read(CONFIGFILE)
        if not config.has_section(SECTION):
            config.add_section(SECTION)
    
    def getLatest(self):
        threads=[]
        try:
            for (user,url,id_,type_) in VIDEO:
                t=Checker(user,url,id_,type_)
                t.setDaemon(True)
                t.start()
                threads.append((t))
            for thread in threads:
                thread.join(60)
            with open(CONFIGFILE,'w') as configfile:
                config.write(configfile)
        except:
            print 'error'

class MyTable(QTableWidget):
    def __init__(self, *args):
        QTableWidget.__init__(self, *args)
        self.thread = VideoThread(self)
        self.thread.dataReady.connect(self.update, Qt.QueuedConnection)
        self.init()
    
    def init(self):
        self.setHorizontalHeaderLabels([u'作者',u'更新时间',u'视频名称',u'视频链接'])
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.cellClicked.connect(self.clik)
    
    def update(self):
        self.setWindowTitle(time.ctime(time.time()))
        row=0
        for (user,_,_,_) in VIDEO:
#             index=0
            for index,info in enumerate(result):
                if user==info[0]:
                    self.insertRow(row)
                    for column in range(4):
                        item = QTableWidgetItem(info[column])
                        if info[4]:
                            item.setForeground(QBrush(QColor(255,0,0)))
                        self.setItem(row, column, item)
                    result.pop(index)
                    break
#                 index+=1
            row +=1
        
#         for info in result:
#             self.insertRow(row)
#             for column in range(4):
#                 item = QTableWidgetItem(info[column])
#                 if info[4]:
#                     item.setForeground(QBrush(QColor(255,0,0)))
#                 self.setItem(row, column, item)
#             row +=1
        self.resizeColumnsToContents()
        self.setFixedSize(self.horizontalHeader().length() + 30, self.verticalHeader().length() + 30); 
        self.show()
        
    def clik(self, row, column):
        print 'clicked',row,column
        if column == 3 :
            item=self.item(row, column)
            if item:
                url=item.text()
                if url.startswith('http://'):
                    webbrowser.open(url)
        if column == 0:
            for (user,url,_,_) in VIDEO:
                if(self.item(row, column).text()==user):
                    webbrowser.open(url)

#     def closeEvent(self, event):
#         event.accept()
#         self.thread.terminate()
#         sys.exit()

class VideoThread(QThread):
    dataReady = Signal(object)
    def run(self):
        print time.ctime(time.time()),u' - 检查视频更新'
        Updater().getLatest()
        self.dataReady.emit('')

if __name__=='__main__':
    app = QApplication(sys.argv)
    table=MyTable(0, 4)
    table.thread.start()
    app.exec_()
    sys.exit()
    
    