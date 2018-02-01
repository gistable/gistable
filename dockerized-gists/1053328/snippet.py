import tornado.ioloop

loop = tornado.ioloop.IOLoop.instance()
def callback(*args):
    loop.add_callback(callback)
callback()
loop.start()