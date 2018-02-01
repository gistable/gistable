#!/usr/bin/python

import math
import pygame
import random
import time
import sys
import array

print """
left-click        place a site
middle-click      recolor a site
right-click       remove a site

If there's only 1 site, draws the distances.
"""

pygame.init()
r = 1
size = WIDTH, HEIGHT = int(500*r), int(500*r)
scr = pygame.display.set_mode(size)



max_size = WIDTH*HEIGHT*4
nan = -0xFFFF #Real distances should be positive anyways.
cache = array.array('i', (nan for _ in range(max_size)))

def memoize(func):
  def memoized_function(x, y):
    key = (x + WIDTH)*2*HEIGHT + (y + HEIGHT)
    val = cache[key]
    if val == nan:
      val = int(func(x, y))
      cache[key] = val
    return val
  return memoized_function

def distance(x, y):
  ##Courtesy of timos, very nice
  #x = x**2
  #y = y**2
  #return x * (1.0 + math.sin(x * 0.001) * 0.2) + y * (1.0 + math.cos(y * 0.001) * 0.2)

  real_dist = math.hypot(x, y)
  #return real_dist
  return real_dist**0.95 + math.sin(real_dist**2/100)*20
  #return real_dist + math.sin(real_dist/1)*10
  #return math.sin(real_dist**2)
  #return abs(x) + abs(y)
  #return (abs(x) + abs(y)) - real_dist
  #return math.log(real_dist + 1)


min_dist = max_dist = None
if 1:
  print "Filling memo cache"
  distance = memoize(distance)
  for x in range(-WIDTH, +WIDTH):
    for y in range(-HEIGHT, +HEIGHT):
      distance(x, y) 
  
  min_dist = min(cache) #Efficiency IV!
  max_dist = max(cache)
  print "range of distance function:", min_dist, max_dist
  dis_dist = max_dist - min_dist
  def normalize(v):
    return (v - min_dist)*0xFF/dis_dist
else:
  normalize = None

class Coord:
  def __init__(self, x=0, y=0):
    self.x = int(x)
    self.y = int(y)
    self.color()

  def color(self):
    self.color = int(random.random()*(2<<32))
    

  def distance(self, other):
    return distance(self.x - other.x, self.y - other.y)

sites = []

pixel = pygame.surfarray.pixels2d(scr)

def draw():
  scr.fill((0x80, 0x80, 0x80))
  print 'drawing'
  start = time.time()
  here = Coord()
  if len(sites) >= 2:
    for x in range(WIDTH):
      for y in range(HEIGHT):
        here.x, here.y = x, y
        min_site = None
        min_dist = sys.maxint
        for site in sites:
          d = here.distance(site)
          if d < min_dist:
            min_site = site
            min_dist = d
        pixel[x][y] = min_site.color
  elif sites and normalize:
    for x in range(WIDTH):
      for y in range(HEIGHT):
        here.x, here.y = x, y
        c = here.distance(sites[0])
        n = normalize(c)
        pixel[x][y] = scr.map_rgb((n, n, n))

  for site in sites:
    r = 2
    for dx in range(-r, r+1):
      for dy in range(-r, r+1):
        if dx == dy == 0:
          pixel[site.x+dx][site.y+dy] = site.color
          continue
        try:
          pixel[site.x+dx][site.y+dy] = 0
        except IndexError: continue

  pygame.display.flip()
  end = time.time()
  print "drawing took", end - start, "with", len(sites), "sitez"

random.seed("secret frame release mind control virus")
if 1:
  sites.append(Coord(WIDTH*0.5, HEIGHT*0.5))
else:
  for _ in range(3):
    sites.append(Coord(random.random()*WIDTH, random.random()*HEIGHT))


draw()
while 1:
  event = pygame.event.wait()
  if event.type == pygame.QUIT: break
  if event.type == pygame.KEYDOWN:
    if event.unicode == u'x':
      sites = []
      draw()
    if event.unicode == u'q':
      print 'bai'
      break
  if event.type == pygame.MOUSEBUTTONDOWN:
    if event.button == 1:
      sites.append(Coord(*event.pos))
    elif sites:
      here = Coord(*event.pos)
      sites.sort(lambda a, b: int(here.distance(a) - here.distance(b)))
      if event.button == 3:
        sites.pop(0)
      else:
        s = sites[0]
        Coord.color(s)
    draw()
  if event.type == pygame.VIDEOEXPOSE:
    draw()
  
import os
os.kill(os.getpid(), 9) #stupid SDL takes forever to close, for me

