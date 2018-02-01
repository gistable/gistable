#!/usr/bin/python2

# Author Tom Fyuri.
# Simple bitcoin usd ticker (btc-e), you're free to modify or share following code however you like.
# Version 0.0.6.

import threading
import pygame
import httplib
import urllib
import json
import time
import sys, os
import copy
from pygame.locals import *

# setup some global stuff
pygame.init()
screen = pygame.display.set_mode((670, 100))
pygame.display.set_caption('BTC-e live ticker')
surface = pygame.Surface(screen.get_size())
surface = surface.convert()
font = pygame.font.Font(None, 34)
font2 = pygame.font.Font(None, 26)
font3 = pygame.font.Font(None, 16)
update_time = 3000
tickrate = 100

class currency_data():
  pass

ticker_data = [["btc_usd","BTC","$","B",currency_data(),0],
	       ["ltc_usd","LTC","$","L",currency_data(),0],
	       ["ltc_btc","LTC","B","L",currency_data(),0]]

def quit():
    pygame.quit(); sys.exit()

def get_price(which): # 
  try:
    conn = httplib.HTTPSConnection("btc-e.com", timeout=4)
    conn.request("GET", "/api/2/"+which+"/ticker")
    response = conn.getresponse()
    j = json.load(response)
    conn.close()
    return j
  except StandardError:
    return None
  
def get_depth(which): # 
  try:
    conn = httplib.HTTPSConnection("btc-e.com")
    conn.request("GET", "/api/2/"+which+"/depth")
    response = conn.getresponse()
    j = json.load(response)
    conn.close()
    return j
  except StandardError:
    return None
  
def process_input():
  key = pygame.key.get_pressed()
  for event in pygame.event.get():
      if event.type == KEYDOWN:
	  if event.key == K_ESCAPE: quit()
	  
def update_data():
  # basic stuff
  for i in ticker_data:
    currency_name = i[0]
    i[5] = copy.deepcopy(i[4]) # save previous?
    pdata = i[5]
    data = i[4]
    data.name = i[1]
    data.nom = i[2]
    data.nom2 = i[3]
    json_data = get_price(currency_name)
    if json_data is None:
      data.error = True
    else:
      data.error = False
      data.buy = json_data['ticker']['buy']
      data.sell = json_data['ticker']['sell']
      data.last = json_data['ticker']['last']
      volume = 0
      #data.volume = json_data['ticker']['vol_cur']
      
      # more interesting thing, fattest walls
      json_data = get_depth(currency_name)
      if json_data is None:
	data.error = True
      else:
	data.error = False
	asks = json_data["asks"]
	bids = json_data["bids"]
	
	best_ask = [asks[0][0],asks[0][1]]
	best_bid = [bids[0][0],bids[0][1]]
	
	for price in asks:
	  volume += best_ask[1]
	  if price[1] >= best_ask[1]:
	    best_ask = price
	for price in bids:
	  volume += best_bid[1]
	  if price[1] >= best_bid[1]:
	    best_bid = price
	    
	data.ask = best_ask
	data.bid = best_bid
	data.volume = volume
	
    if ((hasattr(data,'error')) and (hasattr(pdata,'error')) and (data.error == False) and (pdata.error == False)):
      # update current up/down
      if hasattr(data,'buy_color'):
	data.buy_color = data.buy_color
      else:
	data.buy_color = (250, 250, 250)
      if (data.buy > pdata.buy):
	data.buy_color = (0, 255, 0)
      elif (data.buy < pdata.buy):
	data.buy_color = (255, 0, 0)
	
      if hasattr(data,'sell_color'):
	data.sell_color = pdata.sell_color
      else:
	data.sell_color = (250, 250, 250)
      if (data.sell > pdata.sell):
	data.sell_color = (0, 255, 0)
      elif (data.sell < pdata.sell):
	data.sell_color = (255, 0, 0)
	
      if hasattr(data,'last_color'):
	data.last_color = pdata.last_color
      else:
	data.last_color = (250, 250, 250)
      if (data.last > pdata.last):
	data.last_color = (0, 255, 0)
      elif (data.last < pdata.last):
	data.last_color = (255, 0, 0)
	
      if hasattr(data,'ask_color1'):
	data.ask_color1 = pdata.ask_color1
      else:
	data.ask_color1 = (250, 250, 250)
      if (data.ask[0] > pdata.ask[0]):
	data.ask_color1 = (50, 205, 50)
      elif (data.ask[0] < pdata.ask[0]):
	data.ask_color1 = (215, 50, 50)
      if hasattr(data,'ask_color2'):
	data.ask_color2 = pdata.ask_color2
      else:
	data.ask_color2 = (250, 250, 250)
      if (data.ask[1] > pdata.ask[1]):
	data.ask_color2 = (50, 205, 50)
      elif (data.ask[1] < pdata.ask[1]):
	data.ask_color2 = (215, 50, 50)
	
      if hasattr(data,'bid_color1'):
	data.bid_color1 = pdata.bid_color1
      else:
	data.bid_color1 = (250, 250, 250)
      if (data.bid[0] > pdata.bid[0]):
	data.bid_color1 = (50, 205, 50)
      elif (data.bid[0] < pdata.bid[0]):
	data.bid_color1 = (215, 50, 50)
      if hasattr(data,'bid_color2'):
	data.bid_color2 = pdata.bid_color2
      else:
	data.bid_color2 = (250, 250, 250)
      if (data.bid[1] > pdata.bid[1]):
	data.bid_color2 = (50, 205, 50)
      elif (data.bid[1] < pdata.bid[1]):
	data.bid_color2 = (215, 50, 50)
	
      if hasattr(data,'volume_color'):
	data.volume_color = pdata.volume_color
      else:
	data.volume_color = (250, 250, 250)
      if (data.volume > pdata.volume):
	data.volume_color = (0, 255, 0)
      elif (data.volume < pdata.volume):
	data.volume_color = (255, 0, 0)
	
def redraw():
  surface.fill((0, 0, 0))
  text = font2.render("BTC-E", 1, (250, 250, 250))
  text_pos = text.get_rect(); text_pos.y = 4; text_pos.x = 5;
  surface.blit(text, text_pos)
  text = font.render("last", 1, (250, 250, 250))
  text_pos = text.get_rect(); text_pos.y = 0; text_pos.x = 58+5
  surface.blit(text, text_pos)
  text = font.render("buy", 1, (250, 250, 250))
  text_pos = text.get_rect(); text_pos.y = 0; text_pos.x = 58+115
  surface.blit(text, text_pos)
  text = font.render("sell", 1, (250, 250, 250))
  text_pos = text.get_rect(); text_pos.y = 0; text_pos.x = 58+225
  surface.blit(text, text_pos)
  text = font.render("ask", 1, (250, 250, 250))
  text_pos = text.get_rect(); text_pos.y = 0; text_pos.x = 58+335
  surface.blit(text, text_pos)
  text = font.render("bid", 1, (250, 250, 250))
  text_pos = text.get_rect(); text_pos.y = 0; text_pos.x = 58+425
  surface.blit(text, text_pos)
  text = font.render("volume", 1, (250, 250, 250))
  text_pos = text.get_rect(); text_pos.y = 0; text_pos.x = 58+495
  surface.blit(text, text_pos)
  pos = 25; pos2 = 27;
  for i in ticker_data:
    data = i[4]
    if data.error:
      text = font.render("ERROR", 1, (250, 0, 0))
      text_pos = text.get_rect(); text_pos.y = pos; text_pos.x = 58
      surface.blit(text, text_pos)
    else:
      if (hasattr(data,'last_color')):
	color = data.last_color
      else:
	color = (250, 250, 250)
      text = font2.render("{0}{1}".format(round(data.last,5),data.nom), 1, color)
      text_pos = text.get_rect(); text_pos.y = pos2; text_pos.x = 58
      surface.blit(text, text_pos)
      
      if (hasattr(data,'buy_color')):
	color = data.buy_color
      else:
	color = (250, 250, 250)
      text = font2.render("{0}{1}".format(round(data.buy,5),data.nom), 1, color)
      text_pos = text.get_rect(); text_pos.y = pos2; text_pos.x = 58+110
      surface.blit(text, text_pos)
      
      if (hasattr(data,'sell_color')):
	color = data.sell_color
      else:
	color = (250, 250, 250)
      text = font2.render("{0}{1}".format(round(data.sell,5),data.nom), 1, color)
      text_pos = text.get_rect(); text_pos.y = pos2; text_pos.x = 58+220
      surface.blit(text, text_pos)
      
      if (hasattr(data,'ask_color1')):
	color = data.ask_color1
      else:
	color = (250, 250, 250)
      text = font3.render("{0}{1}".format(round(data.ask[0],5),data.nom), 1, color)
      text_pos = text.get_rect(); text_pos.y = pos2-5; text_pos.x = 58+330+5
      surface.blit(text, text_pos)
      if (hasattr(data,'ask_color2')):
	color = data.ask_color2
      else:
	color = (250, 250, 250)
      text = font3.render("{0}{1}".format(round(data.ask[1],5),data.nom2), 1, color)
      text_pos = text.get_rect(); text_pos.y = pos2+6; text_pos.x = 58+330-1
      surface.blit(text, text_pos)
      
      if (hasattr(data,'bid_color1')):
	color = data.bid_color1
      else:
	color = (250, 250, 250)
      text = font3.render("{0}{1}".format(round(data.bid[0],2),data.nom), 1, color)
      text_pos = text.get_rect(); text_pos.y = pos2-5; text_pos.x = 58+420+5
      surface.blit(text, text_pos)
      if (hasattr(data,'bid_color2')):
	color = data.bid_color1
      else:
	color = (250, 250, 250)
      text = font3.render("{0}{1}".format(round(data.bid[1],2),data.nom2), 1, color)
      text_pos = text.get_rect(); text_pos.y = pos2+6; text_pos.x = 58+420-1
      surface.blit(text, text_pos)
      
      if (hasattr(data,'volume_color')):
	color = data.volume_color
      else:
	color = (250, 250, 250)
      text = font2.render("{0}{1}".format(round(data.volume,2),data.nom2), 1, color)
      text_pos = text.get_rect(); text_pos.y = pos2; text_pos.x = 58+490
      surface.blit(text, text_pos)
      
    # name
    text = font.render(data.name, 1, (250, 250, 250))
    text_pos = text.get_rect(); text_pos.y = pos
    text_pos.x = 5
    surface.blit(text, text_pos)
    
    pos+=25
    pos2+=26
    
  screen.blit(surface, (0, 0))
  pygame.display.flip()

def main():
  clock = pygame.time.Clock()
  update_delay = 0
  update_data()
  redraw()
  while True:
    process_input()
    update_delay = update_delay + tickrate
    if (update_delay >= update_time):
      update_delay = 0
      update_data()
    redraw()
    clock.tick(tickrate)

if __name__ == '__main__': main()