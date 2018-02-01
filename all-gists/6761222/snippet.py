# -*- coding: utf-8 -*-

from math import *
from random import *

### 一次测试 ###
def test():
  speed = 4.0                #初速度
  distance = 0               #已经走过的距离
  threshold = log(50) / 100  #每秒中枪的概率

  while distance < 400:
    distance += speed        #以当前速度移动

    if random() < threshold: #如果中枪，则判断是否死亡，如果不死亡，速度减半
      if speed == 0.5:
        return 0             #死亡！
      else:
        speed /= 2

  return 1                   #成功通过！

### 模拟 ###
succ = 0.0                   #成功次数
times = 100000               #模拟次数，可随需要更改，越大则越准确，但耗时越多
for i in range(0, times):
  if test() == 1:
    succ += 1

print round(succ / times, 2) #成功频率，以此作为概率估算值，结果保留两位小数