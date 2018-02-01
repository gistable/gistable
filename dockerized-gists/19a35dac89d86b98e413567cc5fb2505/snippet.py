#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re
import requests
import Queue
import threading

class Proxy():
    def __init__(self, proxy_url, target_url, ver_keyword, timeout):
        self.proxy_url = proxy_url
        self.target_url = target_url
        self.ver_keyword = ver_keyword
        self.timeout = timeout
        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
        }

    def get(self):
        header = {}
        html = requests.get(self.proxy_url, headers=self.headers).text
        h = re.findall(r'<td.*?>(\d+\.\d+\.\d+\.\d+)</td>\s*<td.*?>(\d+)</td>', html)
        proxies = []
        if len(h) > 0:
            for i in h:
                ip_port = ( "%s:%s" % i).encode('utf-8')
                #todo 验证代理后再append
                proxies.append(ip_port)

        #创建线程,检查代理有效性
        print proxies
        proxy_queue = Queue.Queue()
        threads = []
        for proxy in proxies:
            t = threading.Thread(target=self._check_proxy, args=(proxy, proxy_queue))
            threads.append(t)
            t.start()

        #阻塞,直到所有线程结束
        for t in threads:
            t.join()

        #从队列中取出有效的代理
        available_proxies = []
        while not proxy_queue.empty():
            proxy = proxy_queue.get()
            available_proxies.append(proxy)

        return available_proxies


    def _check_proxy(self, proxy, queue):
        #如果代理有效则加入队列
        try:
            html = requests.get(self.target_url, headers=self.headers, proxies={'http':'http://%s' % proxy}, timeout=self.timeout).text
            h = re.findall(r'%s' % self.ver_keyword, html)
            tip = "未"
            if len(h) > 0:
                queue.put(proxy)
                tip = "已"
            print "[%s]匹配到关键字: %s 个, %s加入代理列表" % (proxy, len(h), tip)
        except Exception:
            pass
            #continue


if __name__ == '__main__':
    proxy_url = "http://www.xicidaili.com/nt/"
    target_url = "http://www.itjuzi.com/company/1"
    ver_keyword = "com_id"
    timeout = 10

    proxy = Proxy(proxy_url, target_url, ver_keyword, timeout)
    l = proxy.get()
    print l