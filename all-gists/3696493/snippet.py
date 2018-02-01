# -*- coding: utf-8 -*-
import urllib, urllib2
import random
import re
from xml.dom import minidom

# Levenshtein Distance 
def lev(first, second):
    """Find the Levenshtein distance between two strings."""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [range(second_length) for x in range(first_length)]
    for i in range(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1][j] + 1
            insertion = distance_matrix[i][j-1] + 1
            substitution = distance_matrix[i-1][j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1][second_length-1]

def query(artist, title):
    ##这里是utf-8编码
    s = urllib.urlopen("http://ttlrcct2.qianqian.com/dll/lyricsvr.dll?sh?Artist=%s&Title=%s&Flags=0" % (ToQianQianHexString(artist), ToQianQianHexString(title))).read()
    doc = minidom.parseString(s)

    result = []
    for e in doc.getElementsByTagName("lrc"):
        l_id = e.getAttribute("id")
        l_artist = e.getAttribute("artist")
        l_title = e.getAttribute("title")
        l_score = lev(artist, l_artist.encode("utf-8")) + \
                  lev(title, l_title.encode("utf-8"))
        result.append((l_score, l_id, l_artist, l_title))
    result.sort()
    return result

def get(Id, artist, title):
    code = CreateQianQianCode(Id, artist, title)
    txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'}
    req = urllib2.Request("http://ttlrcct2.qianqian.com/dll/lyricsvr.dll?dl?Id=%s&Code=%d" % (Id, code), None, txheaders)
    lyric = urllib2.urlopen(req).read()
    return unicode(lyric,'utf-8')

def QianQianStringFilter(string):
    s = string
    s = s.lower()
    s = re.sub('\(.*?\)|\[.*?]|{.*?}|（.*?）', '', s);
    s = re.sub('[ -/:-@[-`{-~]+', '', s);
    # 繁（正）体转换为简体
    s = translate(s,'zh-tw','zh-cn')
    s = unicode(s, 'utf_8')
    s = re.sub(u'[\u2014\u2018\u201c\u2026\u3001\u3002\u300a\u300b\u300e\u300f\u3010\u3011\u30fb\uff01\uff08\uff09\uff0c\uff1a\uff1b\uff1f\uff5e\uffe5]+','',s) 
    return s

def translate(text,lang_from='zh-tw',lang_to='zh-cn'):
    if not text:
        return text
    url = ('http://api.microsofttranslator.com/V2/Ajax.svc/Translate?' +
           'appId=DE2A1CAA235EB52E611BC1243F16E4D301BB600E' +
           '&from='+ lang_from +'&to='+ lang_to +
           '&text='+urllib.quote(text))
    json = urllib.urlopen(url).read()
    p = re.compile('"(.+?)"')
    m = p.search(json)
    return m.group(1)

def ToHexStringUnicode(string):
    s = string
    tmp = ''
    for c in s:
        dec = ord(c)
        tmp += "%02X" % (dec & 0xff)
        tmp += "%02X" % (dec >> 8)
    return tmp

def ToHexString(string):
    tmp = ''
    for c in string:
        tmp += "%02X" % ord(c)
    return tmp

def ToQianQianHexString(string, RequireUnicode = True):
    if RequireUnicode:
        return ToHexStringUnicode(QianQianStringFilter(string))
    else:
        return ToHexString(string)

def Conv(i):
    r = i % 4294967296
    if (i >= 0 and r > 2147483648):
        r = r - 4294967296
    elif (i < 0 and r < 2147483648):
        r = r + 4294967296
    return r

def CreateQianQianCode(lrcId, artist, title):
    lrcId = int(lrcId)

    ##这里需要utf-8编码
    ttstr = ToQianQianHexString((artist + title).encode("utf-8"), False)
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

    t5 = Conv(t2 ^ t3)
    t5 = Conv(t5 + (t1 | lrcId))
    t5 = Conv(t5 * (t1 | t3))
    t5 = Conv(t5 * (t2 ^ lrcId))
    t6 = t5
    if (t6 > 2147483648):
        t5 = t6 - 4294967296
    return t5

if __name__ == "__main__":
    res = query('good coming', '仲間')
    print get(*res[0][1:])