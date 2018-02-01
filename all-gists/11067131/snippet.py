import asyncio

import tornado.concurrent
import tornado.ioloop
import tornado.web
import tornado.platform.asyncio
import tornado.httpclient

class ReqHandler(tornado.web.RequestHandler):
  async def get(self):
    self.write("Hello world!\n")
    print("Hej!")
    await asyncio.sleep(2)
    print("Hej igen!")
    res = await tornado.httpclient.AsyncHTTPClient().fetch("http://google.com")
    print(res)
    self.write("Hello test\n")

app = tornado.web.Application([
  (r'/', ReqHandler)
])

if __name__ == '__main__':
  tornado.platform.asyncio.AsyncIOMainLoop().install()
  app.listen(8080)
  asyncio.get_event_loop().run_forever()
