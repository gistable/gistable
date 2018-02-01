# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import re
import time
import json
import requests

class BaiduFanYiAPI(object):
    """
    api for http://fanyi.baidu.com/

    >>> fy = BaiduFanYiAPI()
    >>> fy.fanyi("百度")
    u'Baidu'
    >>> fy.fanyi("中国")
    u'China'
    """
    def __init__(self):
        self._token = None
        self.reset_token()

    GET_TOKEN_URL = "http://fanyi.baidu.com/"
    TOKEN_RE = re.compile(r'mis\.CONST\.TOKEN="(\w+)";', re.I)
    def reset_token(self):
        r = requests.get(self.GET_TOKEN_URL)
        m = self.TOKEN_RE.search(r.content)
        assert r.status_code == 200
        assert m
        self._token = m.group(1)

    def time(self):
        return int(time.time()*1000)

    TRANS_URL = "http://fanyi.baidu.com/transcontent"
    def fanyi(self, word, f="auto", t="auto"):
        word = word.encode("utf-8") if isinstance(word, unicode) else word
        data = {
                'ie': "utf-8",
                'source': "txt",
                'query': word,
                't': self.time(),
                'token': self._token,
                'from': f,
                'to': t,
                }
        r = requests.post(self.TRANS_URL, data=data)
        assert r.status_code == 200
        r = json.loads(r.content)
        return r['data'][0]['dst']

if __name__ == "__main__":
    import sys
    instance = BaiduFanYiAPI()
    print instance.fanyi(sys.argv[1])
