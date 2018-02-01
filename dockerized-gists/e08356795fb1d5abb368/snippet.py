import redis

r = redis.StrictRedis(host='[cache-name].redis.cache.windows.net', port=6380, db=0, password='[access-key]', ssl=True)
r.set('foo','bar')
result = r.get('foo')

print result