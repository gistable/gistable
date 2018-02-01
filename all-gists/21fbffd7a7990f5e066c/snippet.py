#!/usr/bin/env python

import datetime
from app import app, models
import whoosh
import flask_whooshalchemy


"""
Rebuild all Whoosh search indices

Useful after manually importing data (side-stepping the SQLAlchemy ORM
and automatic Whoosh index updates)

If this is intended as a full rebuild, you should consider deleting the
Whoosh search database (as specified in app.config["WHOOSH_BASE"])
before running the rebuild. This will ensure that no old/stale
data is left in the search indices (this process doesn't delete removed
data, only recreated search entries for current data). 
"""


program_start = datetime.datetime.utcnow()

def log(message):
    logtime = datetime.datetime.utcnow()
    logdiff = logtime - program_start
    print("{0} (+{1:.3f}): {2}".format(logtime.strftime("%Y-%m-%d %H:%M:%S"),
                                    logdiff.total_seconds(),
                                    message))

def rebuild_index(model):
    """Rebuild search index of Flask-SQLAlchemy model"""
    log("Rebuilding {0} index...".format(model.__name__))
    primary_field = model.pure_whoosh.primary_key_name
    searchables = model.__searchable__
    index_writer = flask_whooshalchemy.whoosh_index(app, model)

    # Fetch all data
    entries = model.query.all()

    entry_count = 0
    with index_writer.writer() as writer:
        for entry in entries:
            index_attrs = {}
            for field in searchables:
                index_attrs[field] = unicode(getattr(entry, field))

            index_attrs[primary_field] = unicode(getattr(entry, primary_field))
            writer.update_document(**index_attrs)
            entry_count += 1

    log("Rebuilt {0} {1} search index entries.".format(str(entry_count), model.__name__))

        

if __name__ == "__main__":
    model_list = [models.Product,
                  models.Commodity,
                  models.Category,
                  models.Page]

    for model in model_list:
        rebuild_index(model)
