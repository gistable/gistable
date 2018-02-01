# coding: utf-8
from __future__ import division
import re
import os
import time
import bottle
from xml.dom.minidom import parseString
from math import *

helpstr = '''\
Hi,I'm a calculator bot!
Support:
e, pi, cos, cosh, sin,
sinh, tan, tanh, sqrt,
exp, pow, log, log10,
factorial, acos, acosh,
asin, asinh, atan, atanh

"help" will show this.'''

reply = '''\
<xml>
<ToUserName><![CDATA[{}]]></ToUserName>
<FromUserName><![CDATA[{}]]></FromUserName>
<CreateTime>{}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{}]]></Content>
<FuncFlag>0</FuncFlag>
</xml>'''


def get(dom, att):
    try:
        return dom.getElementsByTagName(att)[0].childNodes[0].data
    except:
        return None


@bottle.get('/')
def index():
    return bottle.request.GET.get('echostr', 'Hello weixin!')


@bottle.post('/')
def calc():
    #raise Exception(str(bottle.request.POST.items()))
    dom = parseString(bottle.request.POST.iterkeys().next())
    toUserName = get(dom, 'ToUserName')
    fromUserName = get(dom, 'FromUserName')
    content = get(dom, 'Content')
    #raise Exception(content)
    try:
        if 'Hello2BizUser' == content:
            res = helpstr
        elif 'help' in content.lower():
            res = helpstr
        else:
            # magic
            content = re.sub(r'(?<=[\d\)])(?=\s[^\)\s\+\-\*\\\/])',
                             ' +', content)
            res = eval(content)
    except Exception as e:
        res = 'input:\n' + content + '\n\nERROR:\n' + (e.message or e.msg)
    return reply.format(fromUserName, toUserName, int(time.time()), res)

if __name__ == "__main__":
    bottle.debug(True)
    bottle.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))