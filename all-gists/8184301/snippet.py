import urlparse

from redis import Redis

from waldo.common import config

conf = config.current()
dbstring = conf['connection_string']
dbstring = urlparse.urlparse(dbstring)
dbstring = "redis://" + dbstring.netloc + ":6329"
redisclient = Redis.from_url(dbstring, db=3)
redisclient.config_set('appendonly', 'yes')
redisclient = redisclient