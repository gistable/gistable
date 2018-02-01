#!/usr/bin/python
"""
Functions are provided for both the DB and NDB Datastore APIs.

References:
 * https://cloud.google.com/appengine/docs/python/datastore/queries
 * https://cloud.google.com/appengine/docs/python/ndb/queries
"""

def db_fetch_all(query, limit=100, cursor=None):
  """Fetch all function for the DB Datastore API."""
  results = []
  more = True
  if cursor:
    query = query.with_cursor(cursor)
  # Fetch entities in batches.
  while more:
    entities = query.fetch(limit)
    results.extend(entities)
    query = query.with_cursor(query.cursor())
    more = bool(entities)
  return results


def ndb_fetch_all(query, limit=100, cursor=None):
  """Fetch all function for the NDB Datastore API."""
  results = []
  more = True
  # Fetch entities in batches.
  while more:
    entities, cursor, more = query.fetch_page(limit, start_cursor=cursor)
    results.extend(entities)
  return results