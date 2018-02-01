# encoding:utf-8

#################################################################################
#自定义区
#beautiful soup doc : http://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html
#################################################################################
DEBUG = False #是否在调试
EXAMPLE_URL = 'http://huaban.com/boards/2904887/' #示例网址
HTML_ENCODING = 'utf8' #返回的encoding,默认就好
IMAGE_DIR = 'image' #存放目录
#################################################################################
#################################################################################

img_host = { 
    "hbimg": "img.hb.aicdn.com",
    "hbfile": "hbfile.b0.upaiyun.com/img/apps" 
}
hbfile = {
     "hbfile": "hbfile.b0.upaiyun.com", 
     "hbimg2": "hbimg2.b0.upaiyun.com"
}


import urllib,urllib2,sys,os,time,json
from bs4 import BeautifulSoup

#页面源码
def request(url,encoding=None):
    '''
    返回页面源码
    '''
    req = urllib2.Request(url) #Request
    res = urllib2.urlopen(req) #open->res
    page = res.read()

    if not encoding == None:
        #已指定encoding
        page = page.decode(encoding)
    return page
#写入一行
def writeLine(f,content):
    '''
    f = open()
    content : Unicode,use utf8 encode
    '''
    f.write(content.encode("utf8") + '\n')
#获取对应的括号位置
def getSecondIndex(template,firstIndex):
    pairs = {
        '{' : '}',
        '(' : ')'
    }
    first = template[firstIndex]
    second = pairs[first]

    count = 1 #firstIndex->first
    remain = template[firstIndex+1:]
    for index in range(len(remain)):
        cur = remain[index]
        if cur == second:
            count-=1
            if count == 0:
                return index+firstIndex+1
        elif cur == first:
            count += 1
    #找不到
    return -1

if DEBUG:   #在debug,取example_url
    argUrl = EXAMPLE_URL
elif len(sys.argv) == 1: #正常运行时,提示帮助信息
    print(u"请指定图片所在网页(如{0})".format(EXAMPLE_URL))
    exit()
else:   #正常指定下载
    argUrl = sys.argv[1] #python [down.py http://xxxx]

if not argUrl.endswith('/'):
    argUrl = argUrl + '/'

'''
1.访问给定地址页,取出20条数据
{
    title : 
    user.username user_id
    pins : [
        {
            pin_id
            file : {
                "bucket": "hbimg",
			    "key": "70633aaf35f9d01f62732993c5d508fb43d94cae9a40-5O3dfy",
			    "type": "image/jpeg",
            }
        }
    ]
}
2.拿到最大的id,max?一页开始&limit=100
3.继续
'''
#解析出网页上js的data
def decodeJson(url):
    html = request(url,"utf8")

    app_index = html.index('app.page["board"]')
    remain = html[app_index:] #去头

    brace_index = remain.index('{')
    remain = remain[brace_index:] #去app[board] =

    rightBraceIndex = getSecondIndex(remain,0) #链接里面有分号&amp;
    remain = remain[:rightBraceIndex+1] #去尾

    return json.loads(remain)
#根据pin获取图片地址
def getFileSrc(pin):
    #pin是json里面的pin
    bucket = pin['file']['bucket']
    key = pin['file']['key']
    base_url = img_host[bucket]
    return "http://{0}/{1}".format(base_url,key)
#根据pin获取图片扩展名,不带.
def getFileExt(pin):
    type = pin['file']['type']
    type = type[type.index('/')+1:] #去掉 image/jpeg 前面的

    type = type.lower()
    if type == 'jpeg' or type == 'pjpeg':
        return 'jpg'
    else :
        return type

data = decodeJson(argUrl)
title = data['title'] #画板名称
username = data['user']['username'] #画板作者
count = data["pin_count"] #图数量

pins = [] #(id,src,ext)
#将data的所有pin添加到pins
def addToPins(data):
    for p in data['pins']:
        pin_id = p["pin_id"]
        pin_src = getFileSrc(p)
        pin_ext = getFileExt(p)

        pin = (pin_id,pin_src,pin_ext)
        global pins
        pins.append(pin)

#首页的pins
addToPins(data)

page_num = count/100 +1 #555个要加载6次
for i in range(1,page_num+1):
    max = pins.pop()[0] #取pins的最后一个的id,同时删除最后一个,后面还要添加它
    url = argUrl + '?max={0}&&limit=101'.format(max)
    data = decodeJson(url)
    addToPins(data)

########################################################################
#pins里面包含数据,开始下载
print(u"图片系列为 : {0}".format(title))
print(u"共{0}张图片,画板作者为 : {1}".format(count,username))
print('')
#image文件夹
if not os.path.exists(IMAGE_DIR):
    os.mkdir(IMAGE_DIR)
#子文件夹
if not os.path.exists(IMAGE_DIR + "/" + title):
    os.mkdir(IMAGE_DIR + "/" + title) #以title新建文件夹

index = 1 #第几张图片
for p in pins:
    #p = (id,src,ext)
    num = "{0:0{1}}".format(index,len(str(count)))
    ext = p[2] #jpg
    src = p[1] #http://xxx
    path = u"{0}/{1}/{2}.{3}".format(IMAGE_DIR,title,num,ext)
    print(u"正在下载第{0}张 : {1}".format(num,src))     
    urllib.urlretrieve(src,path)
    index+=1