
'''
rate_limit2.py

Copyright 2014, Josiah Carlson - josiah.carlson@gmail.com
Released under the MIT license

This module intends to show how to perform standard and sliding-window rate
limits as a companion to the two articles posted on Binpress entitled
"Introduction to rate limiting with Redis", parts 1 and 2:
http://www.binpress.com/tutorial/introduction-to-rate-limiting-with-redis/155
http://www.binpress.com/tutorial/introduction-to-rate-limiting-with-redis-part-2/166

... which will (or have already been) reposted on my personal blog at least 2
weeks after their original binpress.com posting:
http://www.dr-josiah.com

'''

import json
import time

from flask import g, request

def get_identifiers():
    ret = ['ip:' + request.remote_addr]
    if g.user.is_authenticated():
        ret.append('user:' + g.user.get_id())
    return ret


def over_limit(conn, duration=3600, limit=240):
    bucket = ':%i:%i'%(duration, time.time() // duration)
    for id in get_identifiers():
        key = id + bucket

        count = conn.incr(key)
        conn.expire(key, duration)
        if count > limit:
            return True

    return False


def over_limit_multi(conn, limits=[(1, 10), (60, 120), (3600, 240)]):
    for duration, limit in limits:
        if over_limit(conn, duration, limit):
            return True
    return False


def over_limit(conn, duration=3600, limit=240):
    # Replaces the earlier over_limit() function and reduces round trips with
    # pipelining.
    pipe = conn.pipeline(transaction=True)
    bucket = ':%i:%i'%(duration, time.time() // duration)
    for id in get_identifiers():
        key = id + bucket

        pipe.incr(key)
        pipe.expire(key, duration)
        if pipe.execute()[0] > limit:
            return True

    return False


def over_limit_multi_lua(conn, limits=[(1, 10), (60, 120), (3600, 240)]):
    if not hasattr(conn, 'over_limit_lua'):
        conn.over_limit_lua = conn.register_script(over_limit_multi_lua_)

    return conn.over_limit_lua(
        keys=get_identifiers(), args=[json.dumps(limits), time.time()])

over_limit_multi_lua_ = '''
local limits = cjson.decode(ARGV[1])
local now = tonumber(ARGV[2])
for i, limit in ipairs(limits) do
    local duration = limit[1]

    local bucket = ':' .. duration .. ':' .. math.floor(now / duration)
    for j, id in ipairs(KEYS) do
        local key = id .. bucket

        local count = redis.call('INCR', key)
        redis.call('EXPIRE', key, duration)
        if tonumber(count) > limit[2] then
            return 1
        end
    end
end
return 0
'''


def over_limit_sliding_window(conn, weight=1, limits=[(1, 10), (60, 120), (3600, 240, 60)], redis_time=False):
    if not hasattr(conn, 'over_limit_sliding_window_lua'):
        conn.over_limit_sliding_window_lua = conn.register_script(over_limit_sliding_window_lua_)

    now = conn.time()[0] if redis_time else time.time()
    return conn.over_limit_sliding_window_lua(
        keys=get_identifiers(), args=[json.dumps(limits), now, weight])

over_limit_sliding_window_lua_ = '''
local limits = cjson.decode(ARGV[1])
local now = tonumber(ARGV[2])
local weight = tonumber(ARGV[3] or '1')
local longest_duration = limits[1][1] or 0
local saved_keys = {}
-- handle cleanup and limit checks
for i, limit in ipairs(limits) do

    local duration = limit[1]
    longest_duration = math.max(longest_duration, duration)
    local precision = limit[3] or duration
    precision = math.min(precision, duration)
    local blocks = math.ceil(duration / precision)
    local saved = {}
    table.insert(saved_keys, saved)
    saved.block_id = math.floor(now / precision)
    saved.trim_before = saved.block_id - blocks + 1
    saved.count_key = duration .. ':' .. precision .. ':'
    saved.ts_key = saved.count_key .. 'o'
    for j, key in ipairs(KEYS) do

        local old_ts = redis.call('HGET', key, saved.ts_key)
        old_ts = old_ts and tonumber(old_ts) or saved.trim_before
        if old_ts > now then
            -- don't write in the past
            return 1
        end

        -- discover what needs to be cleaned up
        local decr = 0
        local dele = {}
        local trim = math.min(saved.trim_before, old_ts + blocks)
        for old_block = old_ts, trim - 1 do
            local bkey = saved.count_key .. old_block
            local bcount = redis.call('HGET', key, bkey)
            if bcount then
                decr = decr + tonumber(bcount)
                table.insert(dele, bkey)
            end
        end

        -- handle cleanup
        local cur
        if #dele > 0 then
            redis.call('HDEL', key, unpack(dele))
            cur = redis.call('HINCRBY', key, saved.count_key, -decr)
        else
            cur = redis.call('HGET', key, saved.count_key)
        end

        -- check our limits
        if tonumber(cur or '0') + weight > limit[2] then
            return 1
        end
    end
end

-- there is enough resources, update the counts
for i, limit in ipairs(limits) do
    local saved = saved_keys[i]

    for j, key in ipairs(KEYS) do
        -- update the current timestamp, count, and bucket count
        redis.call('HSET', key, saved.ts_key, saved.trim_before)
        redis.call('HINCRBY', key, saved.count_key, weight)
        redis.call('HINCRBY', key, saved.count_key .. saved.block_id, weight)
    end
end

-- We calculated the longest-duration limit so we can EXPIRE
-- the whole HASH for quick and easy idle-time cleanup :)
if longest_duration > 0 then
    for _, key in ipairs(KEYS) do
        redis.call('EXPIRE', key, longest_duration)
    end
end

return 0
'''
