import time
import asyncio
import requests

domain = 'http://integralist.co.uk'
a = '{}/foo?run={}'.format(domain, time.time())
b = '{}/bar?run={}'.format(domain, time.time())

async def get(url):
   print('start: ', url)
   r = requests.get(url)
   print('done: ', url)
   return await asyncio.sleep(0, result=r)

async def get_pages(x, y):
   tasks = [get(x), get(y)]
   done, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED) # also FIRST_EXCEPTION and ALL_COMPLETED (default)
   print('>> done: ', done)
   print('>> pending: ', pending) # will be empty if using default return_when setting

loop = asyncio.get_event_loop()
loop.run_until_complete(get_pages(a, b))
loop.close()