# !/bin/python2

#author: @eligao
#licence: WTFPL http://www.wtfpl.net/

import os
import sys, getopt
from multiprocessing import Pool,freeze_support


#使用方法：先编辑这里再使用，懒得写argc,argv了

#数据文件根目录
folderpath="./"
#工作线程数
#固态硬盘建议填CPU线程数，i7-4700MQ大约可以到200-300M/S的速度
#机械硬盘不要填太大，并发IO数太多反而更慢
maxthreads=2
#要查找的字符串
querystr="dingsanshi"

#已知问题：
#1.以当前目录为根目录时，会查询到本文件
#2.偷懒没有写命令行参数
#3.you tell me

def searchinfile(file):
	ret_val=list()
	print "Searching in:"+file
	for line in open(file,'r').readlines():
		if line.find(querystr)!=-1:
			print "MATCH FOUND:"+line
			ret_val.append(line)
	return ret_val

if __name__ == '__main__':
	#for windows compatibility
	freeze_support()
  #worker pool
	pool=Pool(maxthreads)
  #get file paths list
	filepaths=list()
	for root, _, files in os.walk(folderpath):
		for name in files:
		  filepaths.append(os.path.join(root,name))
	#launch workers
	res=pool.map(searchinfile,filepaths)
	#extract results
	for ls in res:
		for ln in ls:
			print ln

