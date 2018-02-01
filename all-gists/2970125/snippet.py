#coding:utf-8
"""
实现python操作cmd
以及与windows系统交互
"""
import os, sys, subprocess

def pyCmd(cmd):
	cmd = 'dir'
	os.system(cmd)

def startProcess():
	"""
	启动进程，比如dir，call其他bat文件
	"""
	process = subprocess.Popen('chrome',
								shell=True,
								stdout=subprocess.PIPE,
								stderr=subprocess.STDOUT
								)
	(stdoutput, erroutput) = process.communicate()
	return stdoutput

def getReturn(target, useCall=True, useShell=True, cwd=None):
	"""
	获取进程返回信息
	"""
	if useCall:
		target = "call " + target
	process = subprocess.Popen(target,
								shell=useShell,
								cwd=cwd
								)
	process.wait()
	return process.returncode

def killSelf():
	"""
	果断自杀
	"""
	os.remove(sys.argv[0])

getReturn('chrome')