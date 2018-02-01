import tornado.ioloop
import tornado.web
from datetime import datetime
import urlparse
from bson.json_util import dumps

import pymongo
from pymongo import Connection

class Home(tornado.web.RequestHandler):

    def initialize(self, connection):
        self.conn = connection
        self.db = self.conn['blogger']
        self.collection = self.db['blogs']

        ## Blog's Welcome entry
        timestamp = datetime.now()
        blog = {
                "_id": 1,
                "title": "Welcome blog!",
                "tags": ["hello world"],
                "category": ["welcome"],
                "timestamp": timestamp,
        }
        self.db.blogs.insert(blog)

class Blog(Home):

    def get(self, blogid):
        blog = self.db.blogs.find_one({"_id":int(blogid)})
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(blog))
    def post(self):
        _id = self.db.blogs.count() + 1
        timestamp = datetime.now()
        body = urlparse.parse_qs(self.request.body)
        for key in body:
                body[key] = body[key][0]
        blog = {
                "_id": _id,
                "title": body['title'],
                "tags": body['tags'],
                "category": body['category'],
                "timestamp": timestamp
        }
        self.db.blogs.insert(blog)
        location = "/blog/"+ str(_id)
        self.set_header('Content-Type', 'application/json')
        self.set_header('Location', location)
        self.set_status(201)
        self.write(dumps(blog))

    def put(self, blogid):
        ## Convert unicode to int
        _id = int(blogid)
        timestamp = datetime.now()
        body = urlparse.parse_qs(self.request.body)
        for key in body:
                body[key] = body[key][0]
        blog = {
                "title": body['title'],
                "tags": body['tags'],
                "category": body['category'],
                "timestamp": timestamp
        }
        self.db.blogs.update({"_id":_id}, {"$set":blog})
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(blog))

    def delete(self,blogid):
        ## Convert unicode to int
        _id = int(blogid)
        blog = {
                "title": None,
                "tags": [],
                "category": [],
                "timestamp": None,
        }
        self.db.blogs.update({"_id":_id}, {"$set":blog})
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(blog))

class Blogs(Home):

    def get(self):
        blogs = str(list(self.db.blogs.find()))
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(blogs))

    def delete(self):
        blogs = str(list(self.db.blogs.find()))
        self.set_header('Content-Type', 'application/json')
        self.db.blogs.drop()
        self.write(dumps(blogs))

application = tornado.web.Application([
    (r"/", Home),
    (r"/blog/([0-9]+)", Blog, dict(connection = Connection()) ),
    (r"/blog/", Blog, dict(connection =  Connection()) ),
    (r"/blogs/", Blogs, dict(connection =  Connection()) ),
],debug=True)

if __name__ == "__main__":
    application.listen(7777)
    tornado.ioloop.IOLoop.instance().start()
