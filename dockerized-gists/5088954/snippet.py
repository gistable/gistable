#!/usr/bin/python
#-*- coding: utf-8 -*-

'''
http://segmentfault.com/q/1010000000174213

Python验证用户输入IP的合法性，有什么好方法吗？
如：<input type="text" name="ip" id="ip" /> 在text里表单输入的字符串
'''

###########################################################################
# 1. 通过正则表达式判断

import re
 
def ipFormatChk(ip_str):
   pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
   if re.match(pattern, ip_str):
      return True
   else:
      return False

###########################################################################
# 2. 根据ip地址的特性，使用Python内置函数来实现

def ip_check(ip):
    q = ip.split('.')
    return len(q) == 4 and len(filter(lambda x: x >= 0 and x <= 255, \
        map(int, filter(lambda x: x.isdigit(), q)))) == 4

# 上述两种方法仅对ipv4有效
###########################################################################
# 3. 使用第三方库实现
'''
从 Python 3.3 开始标准库中提供了ipaddress模块(http://docs.python.org/dev/library/ipaddress.html#module-ipaddress)，之前的Python版本则可以通过PyPi安装相应的版本(https://pypi.python.org/pypi/ipaddress/1.0.3)。
'''