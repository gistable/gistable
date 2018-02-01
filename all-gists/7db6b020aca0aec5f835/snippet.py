# -*- coding: utf-8 -*-

from hashlib import md5
from urllib import urlencode

#网关
GATEWAY = 'http://wappaygw.alipay.com/service/rest.htm'

class Alipay(object):
    '支付宝移动服务网关'

    def __init__(self, app, key, account):
        self.app = app
        self.key = key
        self.account = account

    def sign(self, p):
        '签名方法'
        keys = p.keys()
        keys.sort()
        s = '&'.join(['%s=%s' % (k, p[k]) for k in keys])
        s += self.key
        if isinstance(s, unicode):
            s = s.encode('utf8')
        hash = md5(s).hexdigest()
        return hash

    def check_sign(self, p):
        '检查签名'
        key = p.pop('sign')
        p.pop('sign_type', '')
        keys = p.keys()
        keys.sort()
        s = '&'.join(['%s=%s' % (k, p[k]) for k in keys])
        s += self.key
        if isinstance(s, unicode):
            s = s.encode('utf8')
        hash = md5(s).hexdigest()
        return key == hash

    def check_notify_sign(self, p):
        '检查主动通知的签名'
        key = p.pop('sign')
        order = ['service', 'v', 'sec_id', 'notify_data']
        s = '&'.join(['%s=%s' % (k, p[k]) for k in order])
        s += self.key
        if isinstance(s, unicode):
            s = s.encode('utf8')
        hash = md5(s).hexdigest()
        return key == hash


    def get_token_xml(self, p):
        '请求中用的XML片段'

        s = ['<direct_trade_create_req>']
        p['pay_expire'] = 24 * 60 * 2 #两天交易关闭
        for f in ['subject', 'out_trade_no', 'total_fee', 'seller_account_name', 'call_back_url', 'notify_url', 'pay_expire']:
            if f in p:
                s.append('<%s>%s</%s>' % (f,
                  p[f].replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if type(p[f]) in [str, unicode] else p[f],
                                          f))

        s.append('</direct_trade_create_req>')
        return ''.join(s)


    def get_token_url(self, p):
        '''获取token的最终地址
        p中的成员参数有:
            - out_trade_no 商户唯一号 (32)
            - subject 标题 (128)
            - total_fee 总金额
            - call_back_url 回调地址
            - notify_url 通知地址
        '''


        req = {}

        req['service'] = 'alipay.wap.trade.create.direct'
        req['format'] = 'xml'
        req['v'] = '2.0'
        req['partner'] = self.app
        req['req_id'] = p['out_trade_no']
        req['sec_id'] = 'MD5'
        p['seller_account_name'] = self.account
        req['req_data'] = self.get_token_xml(p)

        sign = self.sign(req)

        req['sign'] = sign

        for k in req.keys():
            if isinstance(req[k], unicode):
                req[k] = req[k].encode('utf8')

        return GATEWAY + '?' + urlencode(req)


    def get_pay_url(self, token):
        '''获取支付地址'''

        req = {}
        req['service'] = 'alipay.wap.auth.authAndExecute'
        req['format'] = 'xml'
        req['v'] = '2.0'
        req['partner'] = self.app
        req['sec_id'] = 'MD5'
        req['req_data'] = '<auth_and_execute_req><request_token>%s</request_token></auth_and_execute_req>' % token

        sign = self.sign(req)

        req['sign'] = sign

        for k in req.keys():
            if isinstance(req[k], unicode):
                req[k] = req[k].encode('utf8')

        return GATEWAY + '?' + urlencode(req)




if __name__ == '__main__':
    import time
    p = {
        'subject': 'test',
        'out_trade_no': str(int(time.time())),
        'total_fee': '0.01',
        'call_back_url': 'http://www.zouyesheng.com'
    }
    alipay = Alipay('', '', '')
    print alipay.get_token_url(p)
    #print alipay.get_pay_url('')
