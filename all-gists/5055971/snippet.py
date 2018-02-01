import web
import json


urls = (
    '/', 'index',
    '/random', 'random',
    '/dump', 'dump'
)

class index:
    def GET(self):
        return "Hello, web.py!"

class random:
    def GET(self):
        web.header('Content-Type', 'application/json')
        return "{\"random\":\"444\"}"

class dump:
    def GET(self):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')
        import datetime
        now = datetime.datetime.now()
        import random
        rand = 556
        rand = random.randint(0,500)
        data = [ { 'dateTime':str(now), 'random':rand} ]
        data_string = json.dumps(data)
        return data_string

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()