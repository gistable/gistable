#!/usr/bin/python
"""
These commands can be run from the src/script directory, which makes remote_gae availble.
 
Important: Please use the Remote API with extreme caution, since it affects our production servers and Datastore.
Changes made to the production Datastore are often irreparable.
 
References:
 * https://developers.google.com/appengine/articles/remote_api
 * https://developers.google.com/appengine/docs/python/tools/remoteapi
"""
import datetime
 
import remote_gae
remote_gae.fix_path()  # Add src/www to sys.path and setup env.
from google.appengine.ext import ndb

from models import experiments
 
# Connect to production server
remote_gae.configure_gae_with_defaults(local_gae=False)
# Disable caching to ensure fresh results.
ctx = ndb.get_context()
ctx.set_cache_policy(False)
ctx.set_memcache_policy(False)
# Datetime for "recent" models. Datastore uses naive UTC datetimes.
since = datetime.datetime.utcnow() - datetime.timedelta(days=5)
query = experiments.Experiment.query().filter(experiments.Experiment.last_modified > since)

def fetch_all(query, limit=100):
  results = []
  start_dt = datetime.datetime.now()
  # Fetch all entities in batches.
  entities, cursor, more = query.fetch_page(limit)
  while more:
    results.extend(entities)
    entities, cursor, more = query.fetch_page(limit, start_cursor=cursor)
    print len(results), 'entities at', datetime.datetime.now()  # Progress and time tracker.
  results.extend(entities)
  print len(results), 'total entities fetched in', (datetime.datetime.now() - start_dt).seconds, 'seconds'  # Progress and time tracker.
  return results

recent = fetch_all(query)
print len(recent)