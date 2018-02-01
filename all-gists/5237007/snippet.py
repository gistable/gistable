#!/usr/bin/env python
# coding:utf-8
import _env
from time import time
from urllib import urlencode
from urllib2 import urlopen as urlopen2
from urlparse import parse_qsl
from hashlib import md5
from urlgrabber import urlopen
import errno
from json import loads
import socket
import time
import datetime
import httplib
from zapp.SSO.config import OAUTH

def taobao_sign(salt, params):
    for k, v in params.iteritems():
        if type(v) == int:
            v = str(v)
        elif type(v) == float:
            v = '%.2f' % v
        elif type(v) in (list, set):
            v = ','.join([str(i) for i in v])
        elif type(v) == bool:
            v = 'true' if v else 'false'
        elif type(v) == datetime.datetime:
            v = v.strftime('%Y-%m-%d %X')
        if type(v) == unicode:
            params[k] = v.encode('utf-8')
        else:
            params[k] = v
    src = salt + ''.join(
        ["%s%s" %
                        (k, v) for k, v in sorted(params.iteritems())])+salt
    return md5(src).hexdigest().upper()


KEY = OAUTH.TAOBAO.KEY
SECRET = OAUTH.TAOBAO.SECRET

URL = "http://stream.api.taobao.com/stream"

#在完成第一步后还不能接收到任何用户的消息数据，因为数据属于用户，必须获得用户（卖家）的授权允许才能接收用户的数据。所以首先要获取卖家授权即取得sessionkey ，再调用taobao.increment.customer.permit授权获取指定用户的消息。
#在APP运行的过程中，如果APP不再需要接收某个用户的消息，可以调用taobao.increment.customer.stop 取消 。也可以调用taobao.increment.customers.get 查看当前授权接收了那些用户的消息数据。





def taobao_watch():
    begin_time = time.time()
    param = dict(
        timestamp=datetime.datetime.now(),
        app_key=KEY,
    )
    param['sign'] = taobao_sign(OAUTH.TAOBAO.SECRET, param)
    urlopen2(URL, data=urlencode(param)).headers
    s = socket.socket()
    s.connect(('stream.api.taobao.com', 80))
    content = urlencode(param)
    s.send(
        "\r\n".join([
            'POST /stream HTTP/1.0',
            'Content-Type: application/x-www-form-urlencoded',
            'Content-Length: %s' % len(content),
            'Host: stream.api.taobao.com',
            '',
            content
        ])
    )

    s.setblocking(False)
    running = True
    data = ""
    skip = True
    while running:
        try:
            while True:
                data += s.recv(4000)
                if len(data) == 0:
                    running = False
                    break
                while 1:
                    if "\r\n" in data:
                        (line, data) = data.split("\r\n", 1)
                        if skip is True:
                            if not line:
                                skip = False
                        else:
                            line = loads(line)
                            code = line['packet']['code']
                            if code not in (201,200,203):
                                yield line
                    else:
                        break
        except socket.error, e:
            no = e[0]
            if no == errno.EINTR:
                continue
            elif no != errno.EAGAIN :      # Resource temporarily unavailable
                print e
                s.close()
                raise
        if (time.time() - begin_time) > 3600:
            return
        time.sleep(.3)

if "__main__" == __name__:
    for line in taobao_watch():
        print line