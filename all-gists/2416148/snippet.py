"""
Backbone.js handler and mongodb based handler for Tornado.

`BackboneHandler` handles the sync protocol for Backbone.js.  Inherit
from the class and implement the model methods:
    * create_model
    * update_model
    * get_model
    * delete_model
    * get_collection
Optionally implement is_get_collection for complex url routing schemes.

`MongoBackboneHandler` implements these methods using a mongodb database.
Inherit and implement the:
    * model_query
    * collection_query
    * is_get_collection
methods to map url arguments into database queries.  Also optionally implement:
    * before_create
    * before_update
    * validate
To validate and insert data into a document before a create/update

TODO: async version


"""
import json

import tornado.web
import tornado.httpserver
import pymongo
from pymongo.objectid import ObjectId


class BackboneHandler(tornado.web.RequestHandler):

    def initialize(self, auth=True):
        self.auth = auth

    def prepare(self):
        """ authenticate user if required """
        if self.auth:
            if not self.current_user:
                raise tornado.web.HTTPError(403)

    def encode(self, data):
        return json.dumps(data)

    def decode(self, data):
        return self.loads(data)

    # HTTP Verbs / Backbone.js API

    def get(self, *args):
        """ return the collection or a model  """
        if self.is_get_collection(*args):
            self.write(self.encode(self.get_collection(*args)))
        else:
            model = self.get_model(*args)
            if model:
                self.write(self.encode(model))
            else:
                raise tornado.web.HTTPError(404)

    def post(self, *args):
        """ create a model """
        resp = self.create_model(self.decode(self.request.body), *args)
        self.write(json.dumps(resp))

    def put(self, *args):
        """ update a model """
        resp = self.update_model(self.decode(self.request.body), *args)
        self.write(json.dumps(resp))

    def delete(self, *args):
        """ delete a model """
        self.delete_model(*args)


    # Extension points

    def is_get_collection(self, *args):
        """ return true if this get is for a collection """
        return len(args) == 0

    def create_model(self, model, *args):
        """ create model and return a dictionary of updated attributes """
        raise tornado.web.HTTPError(404)

    def get_collection(self, *args):
        """ return the collection """
        raise tornado.web.HTTPError(404)

    def get_model(self, *args):
        """ return a model, return None to indicate not found """
        raise tornado.web.HTTPError(404)

    def update_model(self, model, *args):
        """ update a model """
        raise tornado.web.HTTPError(404)

    def delete_model(self, *args):
        """ delete a model """
        raise tornado.web.HTTPError(404)



class MongoBackboneHandler(BackboneHandler):

    def initialize(self, database=None, **kws):
        BackboneHandler.initialize(self, **kws)
        self.database = database

    # BackboneHandler extension

    def encode(self, data):
        if not isinstance(data, pymongo.cursor.Cursor):
            if '_id' in data:
                data['_id'] = str(data['_id'])
            return json.dumps(data)

        else: # we have a cursor
            data = list(data)
            for d in data:
                if '_id' in d:
                    d['_id'] = str(d['_id'])
            return json.dumps(data)

    def decode(self, data):
        data = json.loads(data)
        if '_id' in data:
            data['_id'] = ObjectId(data['_id'])
        return data

    def create_model(self, model):
        if not self.validate(model):
            raise tornado.web.HTTPError(400)
        updates = self.before_create(model)
        model.update(updates)
        mid = str(self.database.insert(model))
        updates['_id'] = mid
        return updates

    def get_collection(self, *args):
        return self.database.find(self.collection_query(*args))

    def get_model(self, *args):
        return self.database.find_one(self.model_query(*args))

    def update_model(self, model, *args):
        updates = self.before_update(model)
        model.update(updates)
        self.database.update(self.model_query(*args), model)
        return updates

    def delete_model(self, *args):
        self.database.remove(self.model_query(*args))

    # Extension points

    def collection_query(self, *args):
        """ return the query to find a collection from a list of url args """
        return None

    def model_query(self, *args):
        """ return the query to find a model """
        return {'_id': ObjectId(args[-1])}

    def validate(self, model):
        """ return False to to disallow this model """
        return True

    def before_create(self, model):
        """ return any extra attributes you want to add to the model """
        return {}

    def before_update(self, model):
        return {}


if __name__ == "__main__":

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'backbone':


        class TestHandler(BackboneHandler):

            def get_current_user(self):
                """ we want to check auth/noauth """
                return 'test'

            models = [dict(id=str(i), text='X' * i) for i in range(10)]

            def _find(self, cid):
                ms = [x for x in self.models if x['id'] == cid]
                return ms[0] if ms else None

            def create_model(self, model):
                model['id'] = str(max([int(x['id']) for x in self.models]) + 1)
                self.models.append(model)
                print 'created', model
                return dict(id = model['id'])

            def get_collection(self):
                return self.models

            def get_model(self, cid):
                return self._find(cid)

            def update_model(self, model, cid):
                print 'updating', cid, model
                self.models[self.models.index(self._find(cid))] = model

            def delete_model(self, cid):
                print 'deleting'
                self.models.remove(self._find(cid))



        application = tornado.web.Application([
                (r"/api", TestHandler),
                (r"/api/(.+)", TestHandler),
            ],
            debug=True,
            static_path='static',
        )


        application.listen(9999)
        tornado.ioloop.IOLoop.instance().start()

    else:
        import tornado.testing
        import unittest
        import urllib

        class Handler(MongoBackboneHandler):

            def before_create(self, model):
                return dict(created=10)




        class TestMongo(tornado.testing.AsyncHTTPTestCase):

            def setUp(self):
                self.conn = pymongo.Connection()
                self.db = self.conn['bh_test']
                self.coll = self.db['bh_test']
                self.doc = self.coll.insert(dict(a=1, b=2))
                tornado.testing.AsyncHTTPTestCase.setUp(self)

            def tearDown(self):
                tornado.testing.AsyncHTTPTestCase.tearDown(self)
                self.conn.drop_database('bh_test')

            def get_app(self):
                return tornado.web.Application([
                        (r"/api/", Handler, dict(database=self.coll, auth=False)),
                        (r"/api/(.+)", Handler, dict(database=self.coll,
                            auth=False)),
                    ],
                    debug=True,
                    static_path='static',
                )

            def test_get_model(self):
                response = self.fetch('/api/' + str(self.doc), method='GET')
                self.assertEqual(response.code, 200)
                model = json.loads(response.body)
                self.assertEqual(model['_id'],  str(self.doc))
                self.assertEqual(model['a'], 1)

            def test_get_collection(self):
                response = self.fetch('/api/', method='GET')
                self.assertEqual(response.code, 200)
                models = json.loads(response.body)
                self.assertEqual(len(models), 1)
                self.assertEqual(models[0]['a'], 1)

            def test_create_model(self):
                post_args = {'email': 'bro@bro.com'}
                response = self.fetch('/api/', method='POST',
                        body=json.dumps(post_args))
                resp = json.loads(response.body)
                self.assertTrue('_id' in resp)
                self.assertEqual(resp['created'], 10)

            def test_update_model(self):
                response = self.fetch('/api/' + str(self.doc), method='GET')
                self.assertEqual(response.code, 200)
                model = json.loads(response.body)
                model['foo'] = '1234'
                response = self.fetch('/api/' + str(self.doc), method='PUT',
                        body=json.dumps(model))
                self.assertEqual(response.code, 200)
                doc = self.coll.find_one(self.doc)
                self.assertEqual(doc['foo'], '1234')

            def test_delete_model(self):
                response = self.fetch('/api/' + str(self.doc), method='DELETE')
                self.assertEqual(response.code, 200)
                doc = self.coll.find_one(self.doc)
                self.assertEqual(doc, None)


        unittest.main()
