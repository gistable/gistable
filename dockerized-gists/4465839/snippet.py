#!/usr/bin/env python
# http://stackoverflow.com/questions/14180179/eventlet-spawn-doesnt-work-as-expected/14180227#14180227

from flask import Flask
import time
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.debug = True


def background():
    """ do something in the background """
    print('[background] working in the background...')
    time.sleep(2)
    print('[background] done.')
    return 42


def callback(gt, *args, **kwargs):
    """ this function is called when results are available """
    result = gt.wait()
    print("[cb] %s" % result)


@app.route('/')
def index():
    greenth = eventlet.spawn(background)
    print(greenth)
    greenth.link(callback)
    return "Hello World"

if __name__ == '__main__':
    app.run()
