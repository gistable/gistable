#!/usr/bin/env python3

import http.client
import ssl
import urllib.parse


def boxcarpush():
  # Prepare the notification parameters
  params = urllib.parse.urlencode({
  	'user_credentials': 'Your_Access_Token',
  	'notification[title]': 'Menu Alert',
  	'notification[long_message]': 'Chicken and waffles are on the menu today!',
  	'notification[sound]': 'score'})
  
  # Create a secure connection to Boxcar and POST the message
  context = ssl.create_default_context()
  conn = http.client.HTTPSConnection('new.boxcar.io', context=context)
  conn.request('POST', '/api/notifications', params)
  
  # Check the response
  response = conn.getresponse()
  print(response.status, response.reason)
  data = response.read()
  print(data)
  
  # Clean up the connection
  conn.close()




def get_daily_specials():
  return '''Fried green tomatoes,
	    Chicken and waffles,
	    Beef stew,
	    Brussels sprouts,
	    Spam sandwich'''


def main():
  menu = get_daily_specials()
  if 'chicken and waffles' in menu.lower():
    boxcarpush()


if __name__=='__main__':
  main()
