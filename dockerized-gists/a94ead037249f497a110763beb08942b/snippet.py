# coding=utf-8

import time
from datetime import datetime
from threading import Thread

from redis import StrictRedis
from redis.exceptions import ConnectionError


class Console:
    @staticmethod
    def log(log_str):
        print('[%s]%s' % (datetime.now().strftime("%Y-%m-%d %H:%M:%S:%s"), log_str))


class TrashSpider(object):
    def __init__(self, spider_name, redis_uri, queue_name, index_entry, page_reg, monitor_slice=5):
        """
        spider 初始化
        :param spider_name: spider名字
        :param redis_uri: redis连接
        :param queue_name: 存储链接的队列名
        :param index_entry: 爬虫入口
        :param page_reg: 需要下载的页面的正则表达式
        """
        self.spider_name = spider_name
        self.redis_uri = redis_uri
        self.queue_name = queue_name
        # 用于去重爬取过的页面
        self.unique_name = self.queue_name + '_uk'

        self.index_entry = index_entry
        self.page_reg = page_reg
        self.monitor_slice = monitor_slice

        self._redis = StrictRedis(decode_responses=True).from_url(redis_uri)

    def _fetcher_uri(self):
        raise NotImplementedError('This is Abstract Class')

    def _fetch_page(self):
        raise NotImplementedError('This is Abstract Class')

    def _check_redis_alive(self):
        try:
            return self._redis.ping()
        except ConnectionError as e:
            Console.log('[Task:%s] Redis Connection Error' % self.spider_name)
            return False

    def __monitor_thread(self):
        zero_time = 0
        while True:
            now_size = self._redis.llen(self.queue_name)
            Console.log('[Task %s][Monitor] queue size %s' % (self.spider_name, now_size))
            time.sleep(self.monitor_slice)
            if now_size == 0:
                zero_time += 1
            if zero_time > 3:
                Console.log('[Task %s][Monitor] QUIT， QUEUE SIZE 0' % self.spider_name)
                break

    def __run(self):
        self._fetcher_uri()
        self._fetch_page()
        Thread(target=self.__monitor_thread()).start()

    def run(self):
        if not self._check_redis_alive():
            Console.log('[Task:%s] QUIT' % self.spider_name)
            exit(-1)
        if not self.queue_name:
            Console.log('[Task:%s] QUIT, Queue name is None' % self.spider_name)
            exit(-1)
        self.__run()
