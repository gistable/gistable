from google.appengine.ext import db, ndb
from google.appengine.datastore import entity_pb

def db_entity_to_protobuf(e):
    return db.model_to_protobuf(e).Encode()

def protobuf_to_db_entity(pb):
    # precondition: model class must be imported
    return db.model_from_protobuf(entity_pb.EntityProto(pb))

def ndb_entity_to_protobuf(e):
    return ndb.ModelAdapter().entity_to_pb(e).Encode()

def protobuf_to_ndb_entity(pb):
    # precondition: model class must be imported
    return ndb.ModelAdapter().pb_to_entity(entity_pb.EntityProto(pb))

