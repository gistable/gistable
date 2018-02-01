#!/usr/bin/env python
#-*-coding:utf8-*-

"""
vesion2.0

这个脚本的作用是通过输入某首歌页面的url，来实现这首歌的下载，保存到当前工作目录下。
目前可以实现高音质音乐的下载，无须账号登陆。
比如，When I'm Sixty-Four的页面的url是 http://www.xiami.com/song/1003908
download_hq_music('http://www.xiami.com/song/1003908'),将会实现When I'm Sixty-Four的320k版本下载

存在问题：
1.歌曲的封面以及其他id3文件没有下载成功


运行环境：
1.安装python
2.根据已安装python版本在 https://pypi.python.org/pypi/lxml/3.3.5 下载lxml

"""


import os
import urllib
import urllib2
from lxml import etree


def get_song_id(songUrl):
    """
    这个函数的作用是将歌曲地址中包含的歌曲id提前出来，以便转到包含歌曲信息的xml文件中去。
    比如Jeff Buckley地Hallelujah的地址是'http://www.xiami.com/song/1008716?spm=a1z1s.3521865.23309997.23.9M8zJy'
    此函数将中url中提取 1008716
    url中的?spm=a1z1s.3521865.23309997.23.9M8zJy是网站用来统计访问量等信息的字段，不影响程序的运行
    """
    startLocation = len('http://www.xiami.com/song/')
    endLocation = songUrl.find('?spm')
    #考虑到url中可能不带有?spm的可能性：
    if endLocation == -1:
        songId = songUrl[startLocation:]
    else:
        songId = songUrl[startLocation:endLocation]
    return songId





def find_xml(songId):
    """
    这个函数的作用是通过歌曲的id(如Jeff Buckley的Hallelujah的歌曲id为：1008716,可在虾米的网站上看到)找到存放改歌曲信息的xml地址。
    例如Jeff Buckley地Hallelujah的XML的地址为：'http://www.xiami.com/song/playlist/id/1261666/object_name/default/object_id',
    数字部分替换为其他歌曲的songid就可以变成其他歌曲xml文档所在的url。
    另外url最后部分的'/object_name/default/object_id'不影响XML文档的加载
    """
    xmlUrl = 'http://www.xiami.com/song/playlist/id/'+songId
    return xmlUrl





def get_song_info(xmlUrl):
    """
    这个函数的作用是用来解析下面这个网址例如'http://www.xiami.com/song/playlist/id/1008716'这个xml文件中包含的歌曲信息：
    包括歌曲名称、专辑名称、艺术家、专辑存放地址等
    其中location标签下存放的是歌曲的地址，使用了"凯撒阵列"的加密方式，将在另一个函数中进行破解。
    本函数的输入值为XML文件的url，返回值为包含了歌曲众多方面信息的python tuple
    使用了python扩展库lxml进行XML文件的分析
    """
    #通过调用etree来分析xml文件
    tree = etree.parse(xmlUrl)
    #获取xml的根节点
    root = tree.getroot()
    #下面用来获取歌曲信息
    title = root[0][0][0].text
    #print title
    albumName = root[0][0][3].text
    airtist = root[0][0][9].text
    #location是用来记录MP3的地址的，是最为重要的信息
    location = root[0][0][12].text
    return title, albumName, airtist, location





def decode_location(location):
    """
    这个函数的作用是用来破解加密的mp3文件存放地址，
    如Jeff Buckley地Hallelujah的XML的地址为：

    8h2fmF521%2.u371c355EltFii7EF%51mtDed51EE-lt%l.1%52E5ph97fb158%p2ec%5%F813_1bebc9%5%F.
    o2E5172%k%bf3-%5E3mxmF7E%113e553715E-A5i%11756_FyE9fc4E%n%.a2%%8E_la%d725%%5u

    这是一个使用‘凯撒阵列’加密的地址，第一个8表示应该分为8行，从左到右竖着看，可以看到左边开头是http
    8
    h2fmF521%2.u371c355El
    tFii7EF%51mtDed51EE-l
    t%l.1%52E5ph97fb158%
    p2ec%5%F813_1bebc9%5
    %F.o2E5172%k%bf3-%5E
    3mxmF7E%113e553715E-
    A5i%11756_FyE9fc4E%n
    %.a2%%8E_la%d725%%5u
    
    竖着读，再使用urllib2的unquote函数对其进行解密即可，并把^替换成0即可得到真实的mp3下载地址
    """

    #包含地址的字符串长度
    stringLength = len(location)-1
    #获取行数，和列数
    rows = int(location[0])
    columns = stringLength / rows
    #最右边一列的字母数
    rightRows = stringLength % rows
    #去掉开头数字的字符串
    realLocation = location[1:]
    output = ''
    for i in xrange(stringLength):
        x = i %rows
        y = i / rows
        p = 0
        if x <= rightRows:
            p = x * (columns + 1) + y
        else:
            p = rightRows * (columns + 1) + (x - rightRows) *columns + y
        output += realLocation[p]
    #歌曲的实际下载地址
    downloadUrl = urllib2.unquote(output).replace('^', '0')
    return downloadUrl





def get_hq_url(downloadUrl):
    """
    这个函数的作用是把普通音质的地址转换成高音质的地址,
    如如Jeff Buckley地Hallelujah的下载地址经过解密为：
    'http://m5.file.xiami.com/71/10071/50781/1008716_215121_l.mp3?auth_key=910d7e7bb5971dfef3f2c5bb37c5311c-1405900800-0-null'
    其320kbps的下载地址和这个地址略有不同，首先是以m6开头，其次在'.mp3'前将字母l换成h，表示high quality
    所以，该歌曲的320kbps的下载地址为：
    'http://m6.file.xiami.com/71/10071/50781/1008716_215121_h.mp3?auth_key=910d7e7bb5971dfef3f2c5bb37c5311c-1405900800-0-null'
    其url后半段的auth_key暂时还不知道有何作用
    """
    location1 = downloadUrl.find('m5')
    location2 = downloadUrl.find('l.mp3?')
    hqDownloadUrl = downloadUrl[:location1]+'m6'+downloadUrl[(location1+2):location2]+'h.mp3'+downloadUrl[(location2+5):]
    return hqDownloadUrl





def download_hq_music(songUrl):
    """
    此函数的作用是通过虾米页面歌曲地址来下载320kbps音乐，并将其保存在本地。
    存放地址是当前工作空间，文件名为歌曲的名称。
    比如：Jeff Buckley地Hallelujah的歌曲页面为：'http://www.xiami.com/song/1008716?spm=a1z1s.3521865.23309997.23.9M8zJy'
    则download_hq_music('http://www.xiami.com/song/1008716?spm=a1z1s.3521865.23309997.23.9M8zJy')即可使音乐保存到本地
    """
    #获取歌曲的id
    songId = get_song_id(songUrl)
    #通过id找到存放歌曲地址的xml
    xmlUrl = find_xml(songId)
    #获取普通音质歌曲的下载地址
    location = get_song_info(xmlUrl)[3]
    #对下载地址进行解密
    downloadUrl = decode_location(location)
    #获取320kbps下载地址
    hqDownloadUrl = get_hq_url(downloadUrl)
    #获取歌曲名称
    title = get_song_info(xmlUrl)[0]
    #设置歌曲保存地址为当前工作空间
    address = os.getcwd()+'\\'+title+'.mp3'
    urllib.urlretrieve(hqDownloadUrl, address )
    print 'high quality ' + '"' + title +  '"' + ' has been downloaded'


#download_hq_music('http://www.xiami.com/song/1008716?spm=a1z1s.3521865.23309997.23.9M8zJy')
#download_hq_music('http://www.xiami.com/song/1261666?spm=a1z1s.3521865.23309997.2.XdRIhb')
#download_hq_music('http://www.xiami.com/song/1003986?spm=a1z1s.3521865.23309997.180.yzL75K')
#download_hq_music('http://www.xiami.com/song/381573?spm=a1z1s.3521865.23309997.2.tETIlt')

