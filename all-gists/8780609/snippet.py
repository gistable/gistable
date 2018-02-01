script = "\
local current, expected, cur_val, callcount, maxcps \
current = redis.call('GET', KEYS[1]) \
callcount = tonumber(ARGV[1]) \
maxcps = tonumber(ARGV[2]) \
cur_val = 0 \
if current then \
    cur_val = tonumber(current) \
end \
expected = cur_val + callcount \
if expected > maxcps then \
    return nil \
else \
    redis.call('incrby', KEYS[1], callcount) \
    redis.call('expire', KEYS[1], 10) \
    return 1 \
end \
"
is_rate_okay = redisClient.register_script(script)

@task(max_retries=None)
def plivo_call():
    ....
    ....
    call_count = len(ph_list)
    cur_time = timezone.now()
    rate_key = "%s:%s" % (plivo_sub.name, cur_time.strftime("%D %H:%M:%S"))
    ret = is_rate_okay(keys=[rate_key],
              args=[call_count, max_cps])
    if ret is None:
        plivo_call.retry(countdown=randint(60,120))
        return False
    ....
    p = plivo.RestAPI(auth_id,auth_token)
    r = p.make_call(params)
    .....
    ....