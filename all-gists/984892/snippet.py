# -*- coding: utf-8 -*-
"""Efficient django counters that support hundreds updates/sec

Based on Google Appengine sharded counters http://code.google.com/appengine/articles/sharding_counters.html
"""
from django.db import models
from django.db.models import Sum, F
import random
from django.db import transaction, IntegrityError
from django.core.cache import cache

CACHE_KEY = "counter."
CACHE_TIMEOUT = 24 * 60 * 60

class CounterShardConfig(models.Model):
    '''Represents a group of multiple CounterShards'''
    num_shards = models.IntegerField(default=5)
    name = models.CharField(max_length=64, db_index=True, unique=True)

    @staticmethod
    def update(owner_id, owner_type, num_shards=5):
        return CounterShardConfig.get_or_create(owner_id=owner_id,
                                                owner_type=owner_type).\
                                                update(num_shards=num_shards)

    class Meta:
        app_label = "api"

class CounterShard(models.Model):
    '''Holds a value of a counter in the group

    The real value of a counter is sum of all counters in a shard'''
    count = models.IntegerField(default=1)
    name = models.CharField(max_length=64, db_index=True)
    index = models.CharField(max_length=128, db_index=True)

    class Meta:
        unique_together = ('name', 'index')
        app_label = "api"

def get(name):
    '''Returns a counter value for counter name

    Results are cached after first request'''
    result = cache.get(CACHE_KEY + name)
    result = None
    if result is None:
        results = CounterShard.objects.filter(name=name).values()
        result = results.aggregate(count=Sum('count'))['count'] or 0
        cache.add(CACHE_KEY + name, result, CACHE_TIMEOUT)
    return result

def _update(name, delta):
    '''Creates/Updates a counter shard with a new value

    delta will be applied to counter value so make it should be >0
    if you want to increase and <0 to decrease it'''
    sid = transaction.savepoint()
    try:
        config = CounterShardConfig.objects.create(name=name)
        transaction.savepoint_commit(sid)
    except IntegrityError:
        transaction.savepoint_rollback(sid)
        config = CounterShardConfig.objects.get(name=name)
    index = random.randint(0, config.num_shards - 1)
    sid = transaction.savepoint()
    cache_key = CACHE_KEY + name
    try:
        counter = CounterShard.objects.create(name=name,
                                              index=index,
                                              count=delta)
        # if it didn't exist, we just created a counter with count=1
        transaction.savepoint_commit(sid)
    except IntegrityError:
        # if already exists lets just update
        transaction.savepoint_rollback(sid)
        counter = CounterShard.objects.filter(name=name,
                                              index=index)
        counter.update(count=F('count') + delta)
    try:
        if delta > 0:
            cache.incr(cache_key, delta)
        else:
            cache.decr(cache_key, -delta)
    except ValueError:
        # we skip this part if it's not cached yet
        pass
    return True

def inc(name, value=1):
    '''Increase a counter with name for a given value'''
    assert value > 0
    return _update(name, value)

def dec(name, value=1):
    '''Decrease a counter with name for a given value'''
    assert value > 0
    return _update(name, -value)

def remove(name):
    CounterShardConfig.objects.filter(name=name).delete()
    CounterShard.objects.filter(name=name).delete()
    cache.delete(CACHE_KEY + name)
    return True
