# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# unsplash 全站下载脚本
# 请先安装 requests ，BeautifulSoup
# pip install requests beautifulsoup4
# 运行 python unsplash.py
# 输入最小页数和最大页数

import os
import requests
from bs4 import BeautifulSoup	

def unsplash(page):
	headers = {
	'Accept':'*/*; q=0.01',
	'Accept-Encoding':'gzip,deflate',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
	'Cache-Control':'no-cache',
	'Connection':'keep-alive',
	'Referer':'https://unsplash.com/?page={0}'.format(page),
	'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.102 Safari/537.36'
	}
	r = requests.get('https://unsplash.com/?page={0}'.format(page),headers=headers)
	print '爬取第{0}页成功'.format(page)
	soup = BeautifulSoup(r.text)
	urls = soup.select('.photo a')
	pics = []
	for url in urls:
		pics.append(url.get('href'))
	return pics
	
def download(pic):
	headers = {
	'Accept':'*/*; q=0.01',
	'Accept-Encoding':'gzip,deflate',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
	'Cache-Control':'no-cache',
	'Connection':'keep-alive',
	'Referer':'https://unsplash.com/',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.102 Safari/537.36'
	}
	id = pic.split('/')[-2]
	print '开始下载图片 https://unsplash.com/photos/{0}/download'.format(id)
	with open('unsplash/{0}.jpg'.format(id), 'wb') as f:
		f.write(requests.get('https://unsplash.com/photos/{0}/download'.format(id),headers = headers).content)
	
def main():
	minpage = int(raw_input("请输入最小页数（如 1 ）："))
	maxpage = int(raw_input("请输入最大页数（如 47 ）："))+1
	for page in range(minpage,maxpage):
		pics = unsplash(page)
		for pic in pics:
			download(pic)
	print 'OK'

def mkdir(path): 
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
 
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)
 
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        print path+' 创建成功'
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print path+' 目录已存在'
        return False

if __name__ == "__main__":
	mkdir('unsplash')
	main()
