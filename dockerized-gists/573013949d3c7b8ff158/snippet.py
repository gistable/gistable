#!/usr/bin/env python
# coding:utf-8

population = 10000
num_round = 10000

ranks = ["C-","C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S", "S+"]
reward_win  = [20, 15, 12, 12, 10, 10, 10, 10, 10, 5, 3]
reward_lose = [10, 10, 10, 10, 10, 10, 10, 10, 10, 5, 6]
num_ranks = len(ranks)

import random

pop_ranks = [0 for i in xrange(population)]
pop_points = [0 for i in xrange(population)]
for t in xrange(num_round):
  for u in xrange(population):
    if random.random()>0.5: #win
      pop_points[u] += reward_win[pop_ranks[u]]
      if pop_points[u] >= 100:
        if pop_ranks[u] == num_ranks-1: #S+
          pop_points[u] = 99
        else:
          pop_ranks[u]+=1
          pop_points[u]=30
    else: #lose
      pop_points[u] -= reward_lose[pop_ranks[u]]
      if pop_points[u]<0:
        if pop_ranks[u] == 0: #C-
          pop_points[u]=0
        else:
          pop_ranks[u]-=1
          pop_points[u]=70
    #print u, ranks[pop_ranks[u]],pop_points[u]
  if (t%1000)==0:
    for rpop in [(r,pop_ranks.count(r)) for r in range(num_ranks)]:
      print "round",t,":",ranks[rpop[0]], rpop[1]
      
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import matplotlib as mpl
import sys, os, copy, math, re

plt.figure(figsize=(9,6))
plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.15)
plt.rcParams["font.size"]=20
plt.xlabel("ranks")
plt.ylabel("users[%]")
X = range(num_ranks)
Y = [pop_ranks.count(r)*100.0/population for r in X]
plt.xticks(X, ranks)
colors = (0.6,0.6,0.8), (0.3,0.3,0.8), (0.0,0.0,0.8),\
         (0.6,0.9,0.6), (0.3,0.9,0.3),(0.0,0.9,0.0),\
         (0.9,0.9,0.6), (0.9,0.9,0.3),(0.9,0.9,0.0),\
         (0.9,0.45,0.45),(0.9,0.0,0.0),
plt.bar(map(lambda x:x-0.4,X), Y, color=colors)
#plt.legend(loc="upper left")
plt.savefig('ranks.png')
plt.show()

