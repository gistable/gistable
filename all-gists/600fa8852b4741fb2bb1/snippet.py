# This Gist is an alternative to ndb.get_multi which is a lot faster in some circumstances.
# For example, fetching 500 small entities with 90% hit rate is 3x faster than ndb,
# based on my tests in App Engine production environment (F1).
# In general it is worthwhile when fetching a large number of small entities, with >50% memcache hit rate.
# For any keys not in memcache, it falls back on a normal ndb.get_multi

# The code is based on the original ndb.context code, but avoids the task queue overhead.

import logging
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext.ndb.google_imports import entity_pb
from google.appengine.ext.ndb.google_imports import ProtocolBuffer
from google.appengine.ext.ndb import model

def get_multi(keys):
    """ A drop-in replacement of ndb.get_multi.
        This version is much faster when fetching many small objects which are mostly in memcache.
        The two functional differences from ndb are:
          --all keys must belong to the same namespace
          --Doesn't interact with ndb autobatcher.

        Speedup depends on the memcache hit rate:
          100%: 3x faster.
           80%: 1.7x faster.
           50%: about parity.
          <10%: about 20% slower.

        The code is closely based on ndb's own code, but avoids a lot of overhead (seemingly in their task queue code).

    @param keys: list of Keys
    @type keys: ndb.Key
    @return: list of entities
    @rtype: list
    """
    if not keys:
        return

    ctx = ndb.get_context()
    ns = keys[0].namespace()
    # Check single namespace assumption.
    for k in keys:
        if k.namespace() != ns:
            raise ValueError("All keys must belong to a single namespace.")

    # First check the context cache.
    results_from_context_cache = _get_from_context_cache(keys)
    keys_from_context_cache = set([entity.key for entity in results_from_context_cache])

    # Manually get from memcache anything not in context cache.
    mkey_to_key = {key.urlsafe() : key for key in keys if key not in keys_from_context_cache}
    # Strangely memcache.get_multi isn't instant even when key set is empty, so check explicitly.
    if mkey_to_key:
        memcache_response = memcache.get_multi(keys=mkey_to_key.keys(), key_prefix=ctx._memcache_prefix, namespace=ns)
    else:
        memcache_response = {}

    # Any keys that are missing, use ndb to get them from the datastore.
    # Potentially could be faster by also skipping ndb here and doing a lower-level get_multi to the datastore, but too much work.
    keys_to_fetch_from_datastore = [key for mkey, key in mkey_to_key.iteritems() if mkey not in memcache_response and key not in keys_from_context_cache]
    datastore_fetch_futures = ndb.get_multi_async(keys_to_fetch_from_datastore, use_memcache=False)

    # Check if any results appeared in the context cache while memcache RPC was running.
    late_results_from_context_cache = _get_from_context_cache(mkey_to_key.values())
    if late_results_from_context_cache:
        # Drop the corresponding memcache results, no need to deserialize twice.
        for entity in late_results_from_context_cache:
            memcache_response.pop(entity.key.urlsafe(), None)

    # Deserialize the memcache results.
    deserialized_memcache_entities = []
    for mkey, mvalue in memcache_response.iteritems():
      key = mkey_to_key[mkey]
      if mvalue not in (ndb.context._LOCKED, None):
        cls = model.Model._lookup_model(key.kind(), ctx._conn.adapter.default_model)
        pb = entity_pb.EntityProto()
        try:
          pb.MergePartialFromString(mvalue)
        except ProtocolBuffer.ProtocolBufferDecodeError:
          logging.warning('Corrupt memcache entry found '
                          'with key %s and namespace %s' % (mkey, ns))
        else:
          entity = cls._from_pb(pb)
          # Store the key on the entity since it wasn't written to memcache.
          entity._key = key
          if ctx._use_cache(key):
            # Update in-memory cache.
            ctx._cache[key] = entity
          deserialized_memcache_entities.append(entity)

    # Wait for datastore fetch of entities which were not in memcache.
    ndb.Future.wait_all(datastore_fetch_futures)
    entities_from_datastore = map(lambda r : r.get_result(), datastore_fetch_futures)

    # For any keys which were not in memcache, write them to memcache.
    # For a little extra speed, you could make this last call asynchronous and rely on caller to set @ndb.toplevel
    entities_to_write_to_memcache = [e for e in entities_from_datastore if e]
    ndb.put_multi(entities_to_write_to_memcache, use_datastore=False, use_cache=False)

    all_results = (results_from_context_cache + late_results_from_context_cache +
                   deserialized_memcache_entities + entities_from_datastore)

    # Order results to match keys requested.
    key_to_entity = {entity.key : entity for entity in all_results if entity}
    return [key_to_entity.get(k) for k in keys]


def _get_from_context_cache(keys):
    """Get from ndb context cache"""
    ctx = ndb.get_context()
    results = []
    for key in keys:
        if ctx._use_cache(key) and key in ctx._cache:
            entity = ctx._cache[key]
            if entity and entity._key == key:
                results.append(entity)
    return results

def test_get_multi(keys):
    """Check get_multi is identical to ndb get_multi"""
    entities = get_multi(keys)
    ndb_entities = ndb.get_multi(keys)
    returned_entity_keys = set([e.key.id() for e in entities])
    ndb_returned_entity_keys = set([e.key.id() for e in ndb_entities])
    assert(returned_entity_keys == ndb_returned_entity_keys)
