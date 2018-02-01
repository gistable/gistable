# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sae
import web
import json
import urllib2

urls=('/','Index','/xiami/(.+)','Xiami')

class Index:
    def GET(self):
        web.redirect('http://miantiao.me')

class Xiami:
    def GET(self,id):
        id=str(id.replace('.mp3',''))
        request = urllib2.Request(''.join(['http://www.xiami.com/app/iphone/song/id/',id]))
        request.add_header('User-Agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X; en-us) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53')
        request.add_header('Referer', ''.join(['http://www.xiami.com/app/iphone/song/id/',id]))
        response = urllib2.urlopen(request)
        info=json.loads(response.read())
        url=info['location']
        web.seeother(url)
        
app = web.application(urls, globals()).wsgifunc() 
application = sae.create_wsgi_app(app)