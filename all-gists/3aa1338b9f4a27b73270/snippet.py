#!/usr/bin/env python
# encoding: utf-8


"""
@version: 0.3
@author: endoffiht
@file: yunfile_downloader.py
@time: 15/6/29 18:06
"""

import requests
import httplib

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
from pyquery import PyQuery as pq
from urlparse import urlparse
from PIL import Image
import re
import cgi
from progressbar import *
import time
import os
import sys
import getopt


def yun_download(url, background=False, file_path=None, debug=False, auto=False):
    # 显示header
    if debug:
        patch_send()
    print 'Initiate requests.session'
    init()
    download_link, vcode_url = wait_page(url)
    print 'Requseting for vcode'
    vcode = get_vcode(vcode_url, download_link)

    print 'Please wait 30s'

    download_link = download_link[:-5] + '/' + vcode + '.html'
    print 'Download_link with code -->  %s' % download_link

    wait(30)

    print 'Begin download process'

    if background:
        background_download(download_link, file_path, auto)
    else:
        download_page(download_link, file_path, auto)


# 第一步，获取到下一页链接和验证码图片链接
def wait_page(file_url):
    r = s.get(file_url)
    file_url = r.url
    s.get(file_url + '&dr=')
    d = pq(r.text)
    u = urlparse(file_url)
    download_link = ''.join((u.scheme, '://', u.netloc, d('#downpage_link').attr("href")))
    vcode_url = ''.join((u.scheme, '://', u.netloc, '/verifyimg/getPcv.html'))
    return download_link, vcode_url


def auto_upload(dir_name, cmd='/usr/local/bin/python /usr/bin/bypy.py upload'):
    exec_cmd = 'cd {0} && {1}'.format(dir_name, cmd)
    tmp = os.popen(exec_cmd).read()
    print tmp
    sys.exit(0)


def wait(seconds):
    for i in range(0, seconds - 1):
        if i % 5 == 0 or i > seconds - 5:
            print seconds - i
        time.sleep(1)


def background_download(link, file_path, auto):
    try:
        if os.fork() > 0:
            sys.exit(0)
    except OSError, e:
        print 'fork #1 failed: %d (%s)' % (e.errno, e.strerror)
        sys.exit(1)

    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print 'fork #2 failed: %d (%s)' % (e.errno, e.strerror)
        sys.exit(1)

    sys.stdout.flush()
    sys.stderr.flush()
    out_filename = "/tmp/yunfile.log"

    if os.path.exists(out_filename):
        os.system('cat /dev/null > ' + out_filename)
    else:
        os.system('touch ' + out_filename)
    si = file(out_filename, 'r')
    so = file(out_filename, 'a+')
    se = file(out_filename, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    download_page(link, file_path, auto)
    sys.exit(0)


def patch_send():
    old_send = httplib.HTTPConnection.send

    def new_send(self, header):
        print '-----start-----'
        print header
        print '-----end-----'

        return old_send(self, header)  # return is not necessary, but never hurts, in case the library is changed

    httplib.HTTPConnection.send = new_send


def init():
    origin_url = 'http://www.yunfile.com'
    login_url = 'http://www.yunfile.com/view'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
               'Referer': 'http://www.baidu.com/link?url=yRbMCjHoOmVlf-cn9ef'
                          'ZRe0VhjkaYmuUTkDd2O24lyIzP2MRSVV_VfDFS4uiPrC7&wd='
                          '&eqid=cde1aa8f00001b72000000025587c4ff',
               'Connection': 'keep-alive',
               'Cache-Control': 'max-age=0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, sdch',
               'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6'
               }
    global s
    s = requests.session()
    s.headers = headers
    s.get(origin_url)


# 进入下载页
def download_page(download_link, file_path, auto):
    r = s.get(download_link)
    # 需要设置Referer
    s.headers['Referer'] = download_link
    if not r.history:
        # 需要访问这两个网址，可能会得到新的cookie
        urls = re.findall(r'http://www.yunfile.com/ckcounter.jsp[^"]*', r.text)

        for url in urls:
            s.get(url)

        data = {}

        # 用pyquery获取表单很安逸
        d = pq(r.text)
        action = d('#d_down_from').attr('action')

        for x in d('#d_down_from input'):
            x = pq(x)
            key = x.attr('name')
            if key:
                value = x.attr('value')
                data[key] = value

        # 下面两个变量在js脚本里藏着
        data['vid'] = re.search(r'var vericode = "(\w+)"', r.text).group(1)
        data['fileId'] = re.search(r'fileId\.value = "(\w+)";', r.text).group(1)

        # post获取文件，stream需要打开
        r = s.post(action, data, stream=True)

        # 获取文件名
        try:
            value, params = cgi.parse_header(r.headers['content-disposition'])
            file_name = params['filename']

            if file_path:
                # 判断路径存在
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                if file_path[-1] != '/':
                    file_path += '/'

                real_path = file_path + file_name
            else:
                real_path = file_name
            print 'Start downloading ' + real_path
            # 初始化进度条
            print ''
            total = int(r.headers['content-length'])
            widgets = ['Downloading ' + file_name, Percentage(), ' ', Bar(marker=RotatingMarker()),
                       ' ', ETA(), ' ', FileTransferSpeed()]
            pbar = ProgressBar(widgets=widgets, maxval=total).start()

            # 写文件
            with open(real_path, 'wb') as fd:
                progress = 0
                for chunk in r.iter_content(1024):
                    progress += len(chunk)
                    fd.write(chunk)
                    pbar.update(progress)
            pbar.finish()
            print 'Download complete'
            if auto:
                print 'Start upload'
                auto_upload(file_path)
            else:
                sys.exit(0)

        except Exception, e:
            print s.headers
    else:
        print 'Error when downloading'
        print s.headers
        sys.exit(2)


# 获取验证码
def get_vcode(vcode_url, refer):
    # 需要设置Referer
    s.headers['Referer'] = refer
    flag = True
    while (flag):
        r = s.get(vcode_url)
        m_image = Image.open(StringIO(r.content))
        image_to_ascii(m_image)
        # 如果没有pytesseract或者不准备安装，会自动跳过ORC环节
        try:
            import pytesseract
            guess_code = re.sub(r'[\D]', '', pytesseract.image_to_string(m_image, config='digits'))
        except:
            guess_code = None

        # 回车确认  N刷新验证码
        if not guess_code or len(guess_code) != 4:
            ask = 'Please tell me the code  ------> '
        else:
            ask = "vcode == %s ? press enter to confirm,n for refresh or tell me ------> " % guess_code

        code = raw_input(ask)

        if not code:
            break
        elif code.lower() == 'n':
            continue
        else:
            guess_code = code
            flag = False

    return guess_code


# 图片转ASCII码，http://a-eter.blogspot.com/2010/04/image-to-ascii-art-in-python.html
def image_to_ascii(image):
    ascii_chars = ['#', 'A', '@', '%', 'S', '+', '<', '*', ':', ',', '.']

    def image_transfer(image):
        image_as_ascii = []
        all_pixels = list(image.getdata())
        for pixel_value in all_pixels:
            index = pixel_value / 25  # 0 - 10
            image_as_ascii.append(ascii_chars[index])
        return image_as_ascii

    width, heigth = image.size
    new_width = 100
    new_heigth = int((heigth * new_width) / width)
    new_image = image.resize((new_width, new_heigth))
    new_image = new_image.convert("L")  # convert to grayscale
    img_as_ascii = image_transfer(new_image)
    img_as_ascii = ''.join(ch for ch in img_as_ascii)
    for c in range(0, len(img_as_ascii), new_width):
        print img_as_ascii[c:c + new_width]


# 用户登录，待开发
def login():
    pass


def main(argv=None):
    short_opts = 'u:p:dba'
    try:
        optlist, args = getopt.getopt(sys.argv[1:], short_opts)
    except getopt.GetoptError, e:
        print_help()
        sys.exit(2)

    config = dict()
    config['debug'] = False
    config['backgroud'] = False
    config['path'] = None
    config['auto_upload'] = False

    for k, v in optlist:
        if k == '-u':
            config['url'] = v
        if k == '-d':
            config['debug'] = True
        if k == '-b':
            config['backgroud'] = True
        if k == '-p':
            config['path'] = v
        if k == '-a':
            config['auto_upload'] = True

    if 'url' not in config:
        print_help()
        sys.exit(2)

    yun_download(config['url'], config['backgroud'], config['path'], config['debug'], config['auto_upload'])


def print_help():
    print 'help'


if __name__ == '__main__':
    main()
