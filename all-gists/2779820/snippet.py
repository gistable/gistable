#!/usr/bin/python
import json
import bottle
from bottle import static_file, route, run, request, abort, response
import simplejson
import pymongo
from pymongo import Connection
import datetime



class MongoEncoder(simplejson.JSONEncoder):
    def default(self, obj):
                # convert all iterables to lists
        if hasattr(obj, '__iter__'):
            return list(obj)
        # convert cursors to lists
        elif isinstance(obj, pymongo.cursor.Cursor):
            return list(obj)
        # convert ObjectId to string
        elif isinstance(obj, pymongo.objectid.ObjectId):
            return unicode(obj)
        # dereference DBRef
        elif isinstance(obj, pymongo.dbref.DBRef):
            return db.dereference(obj)
        # convert dates to strings
        elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) or isinstance(obj, datetime.time):
            return unicode(obj)
        return simplejson.JSONEncoder.default(self, obj)



connection = Connection('localhost', 27017)
db = connection.mydatabase

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='/home/igs/restlite/static')

@route('/')
def send_static():
    return static_file('index.html',root='/home/igs/restlite/static/')

@route('/equipements', method='PUT')
def put_equipement():
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    entity = json.loads(data)
    if not entity.has_key('_id'):
        abort(400,'No _id specified')
    try:
        db['equipements'].save(entity)
    except ValidationError as ve:
        abort(400, str(ve))

@route('/equipements', method='POST')
def post_equipement():
    data = request.forms

    if not data:
        abort(400, 'No data received')
    entity = {}
    for k,v  in data.items():
        entity[k]=v

    if not entity.has_key('_id'):
        abort(400,'No _id specified')
    try:
        db['equipements'].save(entity)
    except ValidationError as ve:
        abort(400, str(ve))

@route('/equipements/:id', methodd='GET')
def get_equipement(id):
    entity = db['equipements'].find_one({'_id':id})
    if not entity:
        abort(404, 'No equipement with id %s' % id)
    return entity

@route('/equipements', methodd='GET')
def get_equipements():
    entity = db['equipements'].find({})
    if not entity:
        abort(404, 'No equipement')
    response.content_type = 'application/json'
    entries = [entry for entry in entity]
    return MongoEncoder().encode(entries)

run(host='0.0.0.0', port=80)