
'''
rate_limit.py

Written May 7-8, 2014 by Josiah Carlson
Released under the MIT license.

Offers a simple interface for offering rate limiting on a per second, minute,
hour, and day basis. Useful for offering varying rate limits depending on user
behavior. Sliding window based limits offer per minute, hour, and day limits
with per second, minute, and 30-minute precision (respectively).

This probably does what you actually wanted your rate limiter to do, but didn't
realize it, and didn't know how to build it.


Note: this is not Redis-cluster safe due to the generation of keys inside the
Lua script. This could be changed to be Redis Cluster compatible, but would
require porting the core of the algorithm to all client-side languages. I will
leave that as an exercise to the reader.

'''

import time

import redis

SECOND, MINUTE, HOUR, DAY = 1, 60, 3600, 86400

def over_limit_basic(conn, key, limit, duration=MINUTE):
    '''
    Will return whether the count referenced by key has gone over its limit.
    This method uses a fixed schedule where limits are reset at the top of the
    time period.

    On an Intel i7-4770 with 5 clients, you can expect roughly 90k calls/second
    with Redis 2.8.8 (no pipelining, more clients can push this to over 200k
    calls/second).

    Note: you probably want over_limit() or over_limit_sliding() instead.

    Arguments:
        conn - a Redis connection object
        key - a client identification key from which the time-based key will be
              derived
        limit - the number of times that the client can call without going over
                their limit
        duration - how long before we can reset the current request count,
                   defaults to 1 minute (you can pass SECOND, MINUTE, HOUR, or
                   DAY for different time spans)
    '''
    now = time.time()
    key += ':%s'%int(now / duration)
    return conn.pipeline(True) \
        .incr(key) \
        .expire(key, 1 + int(duration - now % duration)) \
        .execute()[-2] > limit

def over_limit(conn, base_keys, second=0, minute=0, hour=0, day=0, weight=1):
    '''
    Will return whether the caller is over any of their limits. Uses a fixed
    schedule where limits are reset at the top of each time period.

    On an Intel i7-4770 with 5 clients, you can expect roughly 60k calls/second
    with Redis 2.8.8 (no pipelining).

    Arguments:
        conn - a Redis connection object
        base_keys - how you want to identify the caller, pass a list of
                    identifiers
        second, minute, hour, day - limits for each resolution
        weight - how much does this "call" count for
    '''
    limits = [second, minute, hour, day, weight, int(time.time())]
    return bool(over_limit_lua(conn, keys=base_keys, args=limits))

def over_limit_sliding(conn, base_keys, minute=0, hour=0, day=0, weight=1):
    '''
    Will return whether the caller is over any of their limits. Uses a sliding
    schedule with millisecond resolution

    On an Intel i7-4770 with 5 clients, you can expect roughly 52k calls/second
    with Redis 2.8.8 (no pipelining).

    Arguments:
        conn - a Redis connection object
        base_keys - how you want to identify the caller, pass a list of
                    identifiers
        second, minute, hour, day - limits for each resolution
        weight - how much does this "call" count for
    '''
    limits = [minute, hour, day, weight, int(time.time())]
    return bool(over_limit_sliding_lua(conn, keys=base_keys, args=limits))

def _script_load(script):
    '''
    Borrowed from my book, Redis in Action:
    https://github.com/josiahcarlson/redis-in-action/blob/master/python/ch11_listing_source.py

    Used because the API for the Python Lua scripting support is awkward.
    '''
    sha = [None]
    def call(conn, keys=[], args=[], force_eval=False):
        if not force_eval:
            if not sha[0]:
                sha[0] = conn.execute_command(
                    "SCRIPT", "LOAD", script, parse="LOAD")
            try:
                return conn.execute_command(
                    "EVALSHA", sha[0], len(keys), *(keys+args))
            except redis.exceptions.ResponseError as msg:
                if not msg.args[0].startswith("NOSCRIPT"):
                    raise
        return conn.execute_command(
            "EVAL", script, len(keys), *(keys+args))
    return call

over_limit_lua = _script_load('''
local slice = {1, 60, 3600, 86400}
local dkeys = {'s', 'm', 'h', 'd'}
local ts = tonumber(table.remove(ARGV))
local weight = tonumber(table.remove(ARGV))
local fail = false

-- only update the counts if all of the limits are okay
for _, ready in ipairs({false, true}) do
    for i = 1, math.min(#ARGV, #slice) do
        local limit = tonumber(ARGV[i])

        -- only check limits that are worthwhile
        if limit > 0 then
            local suff = ':' .. dkeys[i] .. ':' .. math.floor(ts / slice[i])
            local remain = 1 + slice[i] - math.fmod(ts, slice[i])
            for j, k in ipairs(KEYS) do
                local key = k .. suff
                if ready then
                    redis.call('incrby', key, weight)
                    redis.call('expire', key, remain)
                else
                    local total = tonumber(redis.call('get', key) or '0')
                    if total + weight > limit then
                        fail = true
                        break
                    end
                end
            end
        end
    end
    if fail then
        break
    end
end

return fail
''')

over_limit_sliding_lua = _script_load('''
local slice = {60, 3600, 86400}
local precision = {1, 60, 1800}
local dkeys = {'m', 'h', 'd'}
local ts = tonumber(table.remove(ARGV))
local weight = tonumber(table.remove(ARGV))
local fail = false

-- Make two passes, the first to clean out old data and make sure there is
-- enough available resources, the second to update the counts.
for _, ready in ipairs({false, true}) do
    -- iterate over all of the limits provided
    for i = 1, math.min(#ARGV, #slice) do
        local limit = tonumber(ARGV[i])

        -- make sure that it is a limit we should check
        if limit > 0 then
            -- calculate the cutoff times and suffixes for the keys
            local cutoff = ts - slice[i]
            local curr = '' .. (precision[i] * math.floor(ts / precision[i]))
            local suff = ':' .. dkeys[i]
            local suff2 = suff .. ':l'

            -- check each key to verify it is not above the limit
            for j, k in ipairs(KEYS) do
                local key = k .. suff
                local key2 = k .. suff2

                if ready then
                    -- if we get here, our limits are fine
                    redis.call('incrby', key, weight)
                    local oldest = redis.call('lrange', key2, '0', '1')
                    if oldest[2] == curr then
                        redis.call('ltrim', key2, 0, -3)
                        redis.call('rpush', key2, weight + tonumber(oldest[1]), oldest[2])
                    else
                        redis.call('rpush', key2, weight, curr)
                    end
                    redis.call('expire', key, slice[i])
                    redis.call('expire', key2, slice[i])

                else
                    -- get the current counted total
                    local total = tonumber(redis.call('get', key) or '0')

                    -- only bother to clean out old data on our first pass through,
                    -- we know the second pass won't do anything
                    while total + weight > limit do
                        local oldest = redis.call('lrange', key2, '0', '1')
                        if #oldest == 0 then
                            break
                        end
                        if tonumber(oldest[2]) <= cutoff then
                            total = tonumber(redis.call('incrby', key, -tonumber(oldest[1])))
                            redis.call('ltrim', key2, '2', '-1')
                        else
                            break
                        end
                    end

                    fail = fail or total + weight > limit
                end
            end
        end
    end
    if fail then
        break
    end
end

return fail
''')




def test(count=200000):
    import uuid
    keys = [str(uuid.uuid4())]
    c = redis.Redis()

    t = time.time()
    for i in xrange(count):
        over_limit_basic(c, keys[0], 10000)
    print "Basic sequential performance:", count / (time.time() - t)

    t = time.time()
    for i in xrange(count):
        over_limit(c, keys, 10000, 20000)
    print "Fixed sequential performance:", count / (time.time() - t)

    t = time.time()
    for i in xrange(count):
        over_limit_sliding(c, keys, 10000, 20000)
    print "Sliding sequential performance:", count / (time.time() - t)

if __name__ == '__main__':
    test()
