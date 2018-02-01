#!/usr/bin/env python3

"""Copyright (C) 2016 Orzogc

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

import requests
import html2text
from lxml import etree
import html
import json
import math
import os.path
import string
import random
import re

# A岛API文档：https://gist.github.com/anonymous/53b7f88052dd65efb0c21310ccd2a718
# A岛API相关地址
adao_domain = 'h.nimingban.com'
adao_url = 'https://' + adao_domain
adao_appid = 'adao'
adao_get_cookie = adao_url + '/Api/getCookie?appid=' + adao_appid
adao_get_forumlist = adao_url + '/Api/getForumList?appid=' + adao_appid
adao_show_forum = adao_url + '/Api/showf?appid=' + adao_appid
adao_show_thread = adao_url + '/Api/thread?appid=' + adao_appid
adao_show_reference = adao_url + '/Api/ref?appid=' + adao_appid
adao_show_reference2 = adao_url + '/Home/Forum/ref?appid=' + adao_appid
adao_show_feed = adao_url + '/Api/feed?appid=' + adao_appid
adao_add_feed = adao_url + '/Api/addFeed?appid=' + adao_appid
adao_delete_feed = adao_url + '/Api/delFeed?appid=' + adao_appid
adao_reply_thread = adao_url + '/Home/Forum/doReplyThread.html?appid=' +\
    adao_appid
adao_create_thread = adao_url + '/Home/Forum/doPostThread.html?appid=' +\
    adao_appid
adao_search = adao_url + '/Api/search?appid=' + adao_appid

# A岛图片CDN的API，来自https://github.com/seven332/Nimingban
adao_get_cdn = 'https://nimingban.herokuapp.com/get_image_cdn_path'

# A岛串里每页的回复个数
adao_page_reply_num = 19

# 发送图片的Conter-Type
content_type = {'.jpg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif',
                'none': 'application/octet-stream'}


def random_string(size=20, chars=string.ascii_letters + string.digits):
    """生成随机20个字母+数字组合"""
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


class adao_post:
    """A岛发串的POST请求格式"""

    def __init__(self, content, name='', email='', title='',
                 water=True, image=''):
        self.content = content  # 串的内容
        self.name = name  # 串的名称
        self.email = email  # 串的e-mail
        self.title = title  # 串的标题
        self.water = water  # 图片是否有水印
        self.image = image  # 附加图片的本地地址

        self.update_payload()

    def update_payload(self):
        self.payload = [('name', (None, self.name)),
                        ('email', (None, self.email)),
                        ('title', (None, self.title)),
                        ('content', (None, self.content))]

        if self.water:
            self.payload.append(('water', (None, 'true')))

        if self.image:
            extension = os.path.splitext(self.image)[1].lower()
            # 图片名为中文的话会有错误，改为随机名字
            # basename = os.path.basename(self.image)
            basename = random_string() + extension
            self.payload.append(('image', (basename, open(self.image, 'rb'),
                                           content_type[extension])))
        else:
            self.payload.append(('image', ('', '', content_type['none'])))


class adao_post_thread(adao_post):
    """A岛发新串的POST请求格式"""

    def __init__(self, forum_id, *args, **kwargs):
        super(adao_post_thread, self).__init__(*args, **kwargs)
        self.fid = forum_id  # 发新串的版块ID
        self.payload[:0] = [('fid', (None, self.fid))]


class adao_post_reply(adao_post):
    """A岛回复串的POST请求格式"""

    def __init__(self, thread_id, *args, **kwargs):
        super(adao_post_reply, self).__init__(*args, **kwargs)
        self.resto = thread_id  # 要回复的串的ID
        self.payload[:0] = [('resto', (None, self.resto))]


class adao_api:
    """A岛API的封装"""

    def __init__(self):
        self.cookies_file = 'cookies'  # 保存饼干的文件
        self.forumlist_file = 'forumlist'  # 保存A岛各版块信息的文件
        self.headers = {'user-agent': 'HavfunClient-adao'}
        self.timeout = 60.0  # HTTP请求超时的秒数
        self.cookies = []
        self.forumlist = []

        self.session = requests.session()
        self.session.headers.update(self.headers)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    def get_cdn(self):
        """获取A岛图片CDN的地址，设置图片地址"""
        r = self.session.get(adao_get_cdn, timeout=self.timeout)

        self.image_cdn = r.json()[0]['url']  # A岛图片CDN地址
        self.image = self.image_cdn + 'image/'  # A岛图片大图的地址
        self.image_thumb = self.image_cdn + 'thumb/'  # A岛图片略缩图的地址

    def set_cookies_userhash(self, cookie):
        """设置要用哪一个饼干"""
        self.session.cookies.set('userhash', cookie,
                                 domain=adao_domain, discard=False)

    def save_cookie(self, cookie):
        """保存饼干到文件"""
        with open(self.cookies_file, 'at') as f:
            f.write(cookie + '\n')

    def save_all_cookies(self):
        """保存所有饼干到文件"""
        with open(self.cookies_file, 'wt') as f:
            for cookie in self.cookies:
                f.write(cookie + '\n')

    def load_cookies(self):
        """从文件读取饼干
           返回读取到的饼干"""
        try:
            with open(self.cookies_file, 'rt') as f:
                cookies = []
                for cookie in f.readlines():
                    cookies.append(cookie.replace('\n', ''))
                return cookies
        except Exception:
            return []

    def get_cookie(self, save=True):
        """从A岛获取饼干，save为True的话会保存饼干到文件里
           成功的话返回True，失败返回False"""
        self.set_cookies_userhash('')
        r = self.session.get(adao_get_cookie, timeout=self.timeout)
        status = r.json()

        if status == 'ok':
            new_cookie = self.session.cookies.get('userhash')
            self.cookies.append(new_cookie)
            if save:
                self.save_cookie(new_cookie)
            return True
        elif status == 'error':
            return False

    def save_forumlist(self):
        """保存版块信息到文件"""
        with open(self.forumlist_file, 'wt') as f:
            json.dump(self.forumlist, f, ensure_ascii=False, indent=2)

    def load_forumlist(self):
        """从文件读取版块信息
           成功的话返回True，失败就返回False"""
        try:
            with open(self.forumlist_file, 'rt') as f:
                self.forumlist = json.load(f)
            return True
        except Exception:
            return False

    def update_forumlist(self, save=True, convert=True):
        """更新版块信息，save为True的话会保存版块信息到文件
           convert为True的话会转换版块信息的格式"""
        r = self.session.get(adao_get_forumlist, timeout=self.timeout)
        forumlist_detail = r.json()

        if convert:
            for forum_group in forumlist_detail:
                for forum_detail in forum_group['forums']:
                    forum_detail['msg'] = self.convert_content(
                        forum_detail['msg'])

        self.forumlist = forumlist_detail

        if save:
            self.save_forumlist()

    def convert_content(self, content):
        """将HTML格式转换为Markdown格式"""
        return html2text.html2text(html.unescape(content)).replace(
            '\n\n', '').replace('  \n', '\n')

    def show_forum(self, forum_id, page=1, convert=True):
        """获取版面内容，convert为True的话会转换版面内容的格式
           获取成功就返回版面内容，获取失败的话会返回出错信息
           现在A岛API有一个bug，返回的串的五个回复不是最后五个，而是倒数第六至
           第十个回复，如果要获得最后几个回复，请用show_forum2()"""
        payload = {'id': forum_id, 'page': page}
        r = self.session.get(adao_show_forum, params=payload,
                             timeout=self.timeout)
        forum = r.json()

        if type(forum) is str:
            return forum

        if convert:
            for thread in forum:
                thread['content'] = self.convert_content(thread['content'])
                for reply in thread['replys']:
                    reply['content'] = self.convert_content(
                        reply['content'])

        return forum

    def show_forum2(self, forum_id, page=1, reply_num=5, convert=True):
        """获取版面内容，会同时返回每个串的最后reply_num个回复
           convert为True的话会转换版面内容的格式
           获取成功就返回版面内容，获取失败的话会返回出错信息"""
        payload = {'id': forum_id, 'page': page}
        r = self.session.get(adao_show_forum, params=payload,
                             timeout=self.timeout)
        forum = r.json()

        if type(forum) is str:
            return forum

        if convert:
            for thread in forum:
                thread['content'] = self.convert_content(thread['content'])

        for thread in forum:
            last_page = math.ceil(
                int(thread['replyCount']) / adao_page_reply_num)
            thread['replys'] = self.get_last_reply(
                thread['id'], last_page, num=reply_num, convert=convert)

        return forum

    def show_thread(self, thread_id, page=1, convert=True):
        """获取主串的内容，convert为True的话会转换串内容的格式
        获取成功就返回主串内容，获取失败的话会返回出错信息"""
        payload = {'id': thread_id, 'page': page}
        r = self.session.get(adao_show_thread, params=payload,
                             timeout=self.timeout)
        thread = r.json()

        if type(thread) is str:
            return thread

        if convert:
            thread['content'] = self.convert_content(thread['content'])
            for reply in thread['replys']:
                reply['content'] = self.convert_content(reply['content'])

        return thread

    def show_reference(self, post_id, convert=True):
        """获取任意串的内容，convert为True的话会转换串内容的格式
        获取成功就返回串的内容，获取失败的话会返回出错信息"""
        payload = {'id': post_id}
        r = self.session.get(adao_show_reference, params=payload,
                             timeout=self.timeout)
        reference = r.json()

        if type(reference) is str:
            return reference

        if convert:
            reference['content'] = self.convert_content(reference['content'])

        return reference

    def get_reference_thread(self, post_id):
        """获取任意串的主串，返回主串ID"""
        payload = {'id': post_id}
        r = self.session.get(adao_show_reference2, params=payload,
                             timeout=self.timeout)

        p = re.compile('/t/([0-9]+?)\?r=')
        m = p.search(r.text)

        if m is None:
            return "获取引用串的主串失败"
        return m.group()[3:-3]

    def show_reference2(self, post_id, convert=True):
        """获取任意串的内容，convert为True的话会转换串内容的格式
        该函数是直接通过解析网页获得任意串的内容，目前还有一些问题，sage没法判断
        获取成功就返回串的内容，获取失败的话会返回出错信息"""
        payload = {'id': post_id}
        r = self.session.get(adao_show_reference2, params=payload,
                             timeout=self.timeout)
        html = etree.HTML(r.text)
        post = {'admin': '0', 'email': '', 'ext': '', 'img': '', 'sage': '0'}

        post_id2 = html.xpath('//div/@data-threads-id')[0]
        if post_id != post_id2:
            return "该串不存在"

        post['id'] = post_id

        image = html.xpath('/html/body/div/div/div/div/div/a/@href')
        if image:
            p = re.compile('/image/.+')
            post['img'], post['ext'] = os.path.splitext(
                p.search(image[0]).group()[7:])

        post['title'] = html.xpath(
            '//span[@class="h-threads-info-title"]')[0].text
        post['name'] = html.xpath(
            '//span[@class="h-threads-info-email"]')[0].text
        post['now'] = html.xpath(
            '//span[@class="h-threads-info-createdat"]')[0].text
        post['userid'] = html.xpath(
            '//span[@class="h-threads-info-uid"]')[0].text[3:]

        thread_id = html.xpath(
            '//div[@class="h-threads-info"]/a/@href')[0]
        p = re.compile('/t/([0-9]+?)\?r=')
        post['thread_id'] = p.search(thread_id).group()[3:-3]

        content = html.xpath('//div[@class="h-threads-content"]')[0]
        post['content'] = etree.tostring(
            content, encoding='unicode').strip()[37:-12].strip()

        if convert:
            post['content'] = self.convert_content(post['content'])

        if not post['userid']:
            post['admin'] = '1'
            userid = etree.tostring(html.xpath(
                '//span[@class="h-threads-info-uid"]')[0], encoding='unicode')
            post['userid'] = self.convert_content(userid)[3:]

        return post

    def get_last_reply(self, thread_id, last_page, num=5, convert=True):
        """获取某个主串的num个最后回复，convert为True的话会转换回复串内容的格式
           获取成功就返回回复串的内容，获取失败的话会返回出错信息"""
        last_page_detail = self.show_thread(
            thread_id, page=last_page, convert=convert)

        if type(last_page_detail) is str:
            return last_page_detail

        last_page_reply = last_page_detail['replys']
        last_page_num = len(last_page_reply)

        if last_page_num >= num:
            return last_page_reply[-num:]
        elif last_page == 1:
            return last_page_reply
        else:
            last_page_detail2 = self.show_thread(
                thread_id, page=last_page - 1, convert=convert)
            if type(last_page_detail2) is str:
                return last_page_detail2
            return last_page_detail2['replys'][last_page_num - num:] +\
                last_page_reply

    def create_thread(self, forum_id, content, name='', email='', title='',
                      water=True, image=''):
        """在某个版块发表新串，返回True说明发串成功，返回False说明发串失败"""
        post_thread = adao_post_thread(
            forum_id, content=content, name=name, email=email, title=title,
            water=water, image=image)
        r = self.session.post(adao_create_thread, files=post_thread.payload)

        if "发帖成功" in r.text:
            return True
        else:
            return False

    def reply_thread(self, thread_id, content, name='', email='', title='',
                     water=True, image=''):
        """回复某个主串，返回True说明回复成功，返回False说明回复失败"""
        post_reply = adao_post_reply(
            thread_id, content=content, name=name, email=email, title=title,
            water=water, image=image)
        r = self.session.post(adao_reply_thread, files=post_reply.payload)

        if "回复成功" in r.text:
            return True
        else:
            return False

    def show_feed(self, uuid, page=1, convert=True):
        """获取订阅内容，uuid为自定义的字母+数字组合，以识别不同的订阅
           convert为True的话会转换订阅串内容的格式
           返回订阅内容"""
        payload = {'uuid': uuid, 'page': page}
        r = self.session.get(adao_show_feed, params=payload,
                             timeout=self.timeout)
        feed_thread = r.json()

        if not feed_thread:
            return feed_thread

        if convert:
            for thread in feed_thread:
                thread['content'] = self.convert_content(thread['content'])

        return feed_thread

    def add_feed(self, uuid, thread_id):
        """订阅某个串，uuid为自定义的字母+数字组合，以识别不同的订阅
           返回True说明订阅成功，返回False说明订阅失败"""
        payload = {'uuid': uuid, 'tid': thread_id}
        r = self.session.get(adao_add_feed, params=payload,
                             timeout=self.timeout)

        if '\\u8ba2\\u9605\\u5927\\u6210\\u529f' in r.text:
            return True
        else:
            return False

    def delete_feed(self, uuid, thread_id):
        """取消订阅某个串，uuid为自定义的字母+数字组合，以识别不同的订阅
           返回True说明取消订阅成功，返回False说明取消订阅失败"""
        payload = {'uuid': uuid, 'tid': thread_id}
        r = self.session.get(adao_delete_feed, params=payload,
                             timeout=self.timeout)

        if '\\u53d6\\u6d88\\u8ba2\\u9605\\u6210\\u529f' in r.text:
            return True
        else:
            return False

    def search(self, keyword, page=1, convert=True):
        """搜索串的内容，convert为True的话会转换搜索返回内容的格式
        返回搜索到的串"""
        payload = {'q': keyword, 'pageNo': page}
        r = self.session.get(adao_search, params=payload, timeout=self.timeout)
        result = r.json()

        if convert:
            for post in result['hits']['hits']:
                post['_source']['content'] = self.convert_content(
                    post['_source']['content'])

        return result


def main():
    # 示例代码
    from pprint import pprint
    with adao_api() as adao:
        # 自定义订阅uuid，不同的uuid订阅内容是不同的
        uuid = random_string()
        pprint(uuid)
        # 获取A岛图片CDN的地址
        adao.get_cdn()

        # 读取饼干
        adao.cookies = adao.load_cookies()
        if adao.cookies:
            # 设置用哪一个饼干
            adao.set_cookies_userhash(adao.cookies[0])
        else:
            # 没有饼干，尝试能不能拿到饼干
            if adao.get_cookie():
                pprint("拿到饼干")
            else:
                pprint("没有饼干")
        pprint(adao.cookies)

        # 读取版块信息
        if not adao.load_forumlist():
            adao.update_forumlist()
        pprint(adao.forumlist)

        # 读取综1的ID
        for forum_group in adao.forumlist:
            for forum_detail in forum_group['forums']:
                if forum_detail['name'] == "综合版1":
                    forum_id = forum_detail['id']

        # 获取综1第一页的串
        forum = adao.show_forum(forum_id=forum_id, page=1)
        pprint(forum)

        # 获取某串的第一页内容
        thread = adao.show_thread('10868852', page=1)
        pprint(thread)

        # 获取任意串的内容
        post = adao.show_reference('10905357')
        pprint(post)

        # 获取任意串的主串ID
        post_thread_id = adao.get_reference_thread('10905357')
        pprint(post_thread_id)

        # 获取串的图片地址
        if post['img']:
            post_image = adao.image + post['img'] + post['ext']
            post_image_thumb = adao.image_thumb + post['img'] + post['ext']
        pprint((post_image, post_image_thumb))

        # 回复某个串
        if adao.reply_thread('10868852', 'test蛤'):
            pprint("回复成功")

        # 下面是发表新串的代码，请自行取消注释运行
        # 综1限制30秒发一次串
        # from time import sleep
        # sleep(30.0)
        # 在综1发新串
        # if adao.create_thread(forum_id, 'test蛤'):
        #    pprint("发新串成功")

        # 添加订阅某个串
        if adao.add_feed(uuid, '10868852'):
            pprint("订阅成功")
        # 获取订阅内容的第一页
        feed = adao.show_feed(uuid, page=1)
        pprint(feed)
        # 取消订阅某串
        if adao.delete_feed(uuid, '10868852'):
            pprint("取消订阅成功")

        # 搜索某些内容
        result = adao.search('acfun')
        pprint(result)


if __name__ == '__main__':
    main()
