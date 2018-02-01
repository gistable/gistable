# -*- coding: utf-8 -*-
import encodings.utf_8
import math
import urllib, urllib2
import random
import re
from xml.dom import minidom
from LevenshteinDistance import LevenshteinDistance
from grabber import LyricProviderBase



class TTPlayerCNC(LyricProviderBase):
    def GetName(self):
        return "千千静听（LRC）"
    
    def GetDescription(self):
        return "从千千静听服务器下载歌词（LRC）"

    def GetURL(self):
        return "http://www.ttplayer.com"

    def GetVersion(self):
        return "0.3"

    def Query(self, handles, status, abort):
        result = []

        for handle in handles:
            status.Advance()

            if abort.Aborting():
                return result

            try:
                artist = handle.Format("[%artist%]")
                title = handle.Format("[%title%]")
                s = urllib.urlopen("http://ttlrcct2.qianqian.com/dll/lyricsvr.dll?sh?Artist=%s&Title=%s&Flags=0" % (self.ToQianQianHexString(artist), self.ToQianQianHexString(title))).read() ##这里是utf-8编码
                doc = minidom.parseString(s)
                m = 0xFFFFFFFFFFFFFFFF
                best = None
                
                for e in doc.getElementsByTagName("lrc"):
                #    i = LevenshteinDistance(artist, e.getAttribute("artist")) + LevenshteinDistance(title, e.getAttribute("title"))#原来对比的是不同编码的文本
                    i = LevenshteinDistance(artist, e.getAttribute("artist").encode("utf-8")) + LevenshteinDistance(title, e.getAttribute("title").encode("utf-8"))   
                    if m > i:
                        m = i
                        best = e.getAttribute("id"), e.getAttribute("artist"), e.getAttribute("title")
            
                if best == None:
                    result.append('')
                    continue
                
                Id, artist, title = best
                code = self.CreateQianQianCode(Id, artist, title)
                txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'}
                req = urllib2.Request("http://ttlrcct2.qianqian.com/dll/lyricsvr.dll?dl?Id=%s&Code=%d" % (Id, code), None, txheaders)
                lyric = urllib2.urlopen(req).read()
                
                if lyric.find("Search ID or Code error!") >= 0:
                    result.append('')
                    continue
                else:
                    result.append(lyric)
            except Exception, e:
                traceback.print_exc(file=sys.stdout)
                result.append('')
                continue

        return result

    def QianQianStringFilter(self,string):
        s = string
        # 英文转小写
        s = s.lower()
        # 去括号，大中小还有全角的小括号
        s = re.sub('\(.*?\)|\[.*?]|{.*?}|（.*?）', '', s);
        # 去除半角特殊符号，空格，逗号，etc。
        s = re.sub('[ -/:-@[-`{-~]+', '', s);
        # 繁（正）体转换为简体
        s = translate(s,'zh-tw','zh-cn') # 并不完美.比如千千静听的後(/u8C5F)字没有转换
        s = unicode(s, 'utf_8')
        # 去除全角特殊符号
        s = re.sub(u'[\u2014\u2018\u201c\u2026\u3001\u3002\u300a\u300b\u300e\u300f\u3010\u3011\u30fb\uff01\uff08\uff09\uff0c\uff1a\uff1b\uff1f\uff5e\uffe5]+','',s) 
        return s
    def ToHexStringUnicode(self, string):
        s = string

        tmp = ''
        for c in s:
            dec = ord(c)
            tmp += "%02X" % (dec & 0xff)
            tmp += "%02X" % (dec >> 8)
        return tmp

    def ToHexString(self, string):
        tmp = ''
        for c in string:
            tmp += "%02X" % ord(c)
        return tmp

    def ToQianQianHexString(self, string, RequireUnicode = True):
        if RequireUnicode:
            return self.ToHexStringUnicode(self.QianQianStringFilter(string))
        else:
            return self.ToHexString(string)

    def Conv(self, i):
        r = i % 4294967296
        if (i >= 0 and r > 2147483648):
            r = r - 4294967296
        elif (i < 0 and r < 2147483648):
            r = r + 4294967296
        return r

    def CreateQianQianCode(self, lrcId, artist, title):
        lrcId = int(lrcId)
        ttstr = self.ToQianQianHexString((artist + title).encode("utf-8"), False) ##这里需要utf-8编码
        length = len(ttstr) >> 1
        song = []

        for i in xrange(length):
            song.append(int(ttstr[i*2:i*2+2], 16))
        t1 = 0
        t2 = 0
        t3 = 0
        t1 = (lrcId & 0x0000FF00) >> 8
        if (lrcId & 0x00FF0000) == 0:
            t3 = 0x000000FF & ~t1
        else:
            t3 = 0x000000FF & ((lrcId & 0x00FF0000) >> 16)

        t3 |= (0x000000FF & lrcId) << 8
        t3 <<= 8
        t3 |= 0x000000FF & t1
        t3 <<= 8

        if (lrcId & 0xFF000000) == 0:
            t3 |= 0x000000FF & (~lrcId)
        else:
            t3 |= 0x000000FF & (lrcId >> 24)

        j = length - 1
        
        while j >= 0:
            c = song[j]
            if c >= 0x80:
                c = c - 0x100
            t1 = (c + t2) & 0x00000000FFFFFFFF
            t2 = (t2 << (j % 2 + 4)) & 0x00000000FFFFFFFF
            t2 = (t1 + t2) & 0x00000000FFFFFFFF
            j -= 1

        j = 0
        t1 = 0

        while j <= length - 1:
            c = song[j]
            if c >= 0x80: # c <128
                c = c - 0x100
            t4 = (c + t1) & 0x00000000FFFFFFFF
            t1 = (t1 << (j % 2 + 3)) & 0x00000000FFFFFFFF
            t1 = (t1 + t4) & 0x00000000FFFFFFFF
            j += 1

        t5 = self.Conv(t2 ^ t3)
        t5 = self.Conv(t5 + (t1 | lrcId))
        t5 = self.Conv(t5 * (t1 | t3))
        t5 = self.Conv(t5 * (t2 ^ lrcId))
        t6 = t5
        if (t6 > 2147483648):
            t5 = t6 - 4294967296
        return t5

def translate(text,lang_from,lang_to):
    #Out of Date
    #v2 居然要收錢,還這麼貴 see:http://code.google.com/apis/language/translate/v2/pricing.html
    #url = ('http://ajax.googleapis.com/ajax/services/language/translate?' +
    #         'v=1.0&q='+urllib.quote(text)+'&langpair='+lang_from+'%7C'+lang_to)
    # 替換成bing的翻譯api
    url = ('http://api.microsofttranslator.com/V2/Ajax.svc/Translate?' +
           'appId=DE2A1CAA235EB52E611BC1243F16E4D301BB600E' +
           '&from='+ lang_from +'&to='+ lang_to +
           '&text='+urllib.quote(text))
    json = urllib.urlopen(url).read()
    #    return json;
    #  p = re.compile('"translatedText":"(.+?)"')  #對應谷歌
    p = re.compile('"(.+?)"') #對應必應
    m = p.search(json);
    return m.group(1);

if __name__ == "__main__":
    LyricProviderInstance = TTPlayerCNC()