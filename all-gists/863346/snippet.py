import redis
import time
from contextlib import contextmanager
class _LockFailedError(Exception): pass

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# there's a bug in redis-py
def _my_parse_info(response):
    "Parse the result of Redis's INFO command into a Python dict"
    info = {}
    def get_value(value):
        if ',' not in value:
            return value
        sub_dict = {}
        for item in value.split(','):
            k, v = item.rsplit('=', 1)
            try:
                sub_dict[k] = int(v)
            except ValueError:
                sub_dict[k] = v
        return sub_dict
    for line in response.splitlines():
        key, value = line.split(':')
        try:
            info[key] = float(value) if '.' in value else int(value)
        except ValueError:
            info[key] = get_value(value)
    return info

redis.client.Redis.RESPONSE_CALLBACKS['INFO'] = _my_parse_info

class MultiLockRedis(redis.client.Redis):
    MASTER_LOCK_KEY = '_multi_lock_global_lock'
    MASTER_SERVER_KEY = '_master_server'
    MASTER_SERVER_VERSION_KEY = '_master_server_version' # we need to use versioning to make a server have precedence if it went down

    def __init__(self, connection_dicts):
        redis.client.Redis.__init__(self)
        self.connection_dicts = connection_dicts
        self.master_server = None

        self._determine_master()

            


    def _determine_master(self):
        with self._global_lock:

            last_master_dict = self.master_server

            master_dict = None
            master_version = -1

            highest_version_seen = -1

            # first we go through all the servers and see who they think the master is.
            for connection_dict in self.each_alive_connection():
                
                # we want to make it so if no redis server has been initialized, the master_dict is set to the first alive one in the list
                if master_dict is None:
                    master_dict = connection_dict

                tmp_master_dict = self.hgetall(self.MASTER_SERVER_KEY)

                if tmp_master_dict:
                    tmp_master_version = long(self.get(self.MASTER_SERVER_VERSION_KEY))

                    # save the highest_version_seen in case we don't have any alive connections
                    highest_version_seen = max(tmp_master_version, highest_version_seen)

                    # if the version we see is higher than the highest version we've seen
                    # check if that server is still alive
                    if tmp_master_version > master_version and \
                       self.connection_dict_is_alive(tmp_master_dict):
                        master_dict = tmp_master_dict
                        master_version = tmp_master_version

            master_dict['port'] = int(master_dict['port'])
            master_dict['db'] = int(master_dict['db'])

            self.master_server = master_dict

            logging.info("Setting master to %s", master_dict)

            self.select(**self.master_server)

            # set the master server to be SLAVEOF NO ONE (master)
            self.slaveof()

            # set the appropriate values on the master for 
            self.set(self.MASTER_SERVER_VERSION_KEY, master_version)
            self.delete(self.MASTER_SERVER_KEY)
            self.hmset(self.MASTER_SERVER_KEY, self.master_server)
            
            master_version = highest_version_seen + 1
            
            master_host = self.master_server['host'] 
            master_port = self.master_server['port']

            for connection_dict in self.each_alive_connection():
                self.set(self.MASTER_SERVER_VERSION_KEY, master_version)
                self.delete(self.MASTER_SERVER_KEY)
                self.hmset(self.MASTER_SERVER_KEY, self.master_server)

                # now set all the slaves
                if connection_dict != self.master_server:
                    logging.info("Setting master key on %s to %s", connection_dict, master_dict)
                    
                    info = self.info()
                    if info.get('master_host', None) != master_host or \
                       int(info.get('master_port', -1)) != master_port:

                        logging.info("Setting SLAVEOF key on %s to %s:%s", connection_dict, master_host, master_port)
                        self.slaveof(master_host, master_port)
                
            

                    
    def connection_dict_is_alive(self, connection_dict):
        try:
            with self.temp_connection(connection_dict):
                self.ping()
        except redis.exceptions.RedisError:
            return False
        return True

    def each_alive_connection(self):
        """
        This basically goes through each connection and yields the ones that are reachable
        """
        for connection_dict in self.each_connection():
            try:
                self.ping()
                yield connection_dict
            except redis.exceptions.RedisError, e:
                pass

        


    def each_connection(self):
        """
        Yield while each of our connections are selected and chosen
        """
        for cd in self.connection_dicts:
            with self.temp_connection(cd) as connection:
                yield cd

    
    @property
    def _global_lock(self):
        return self.multi_lock("_multi_lock_global_lock", timeout=30)

    @contextmanager
    def temp_connection(self, connection_dict):
        old_connection = self.connection
        self.select(**connection_dict)
        yield self.connection
        self.connection = old_connection

    def multi_lock(self, name, timeout, sleep=0.1):
        """
        require a timeout so we don't get into a deadlock situation
        """
        return MultiLock(self, name, timeout, sleep)



class MultiLock(object):
    def __init__(self, redis, name, timeout=None, sleep=0.1):
        self.redis = redis
        self.timeout = timeout
        self.sleep = sleep
        self.name = name
        self.locks = [(cd, self._make_lock(cd)) for cd in self.redis.each_alive_connection()]
        assert(self.locks) # make sure the size is greater than one

    def acquire(self, blocking=True):
            return self._inner_acquire(blocking)
                
    def _inner_acquire(self, blocking):
        locked_locks = []
        try:
            for cd, lock in self.locks:
                with self.redis.temp_connection(cd):
                    if lock.acquire(blocking):
                        # if we acquire it, save it
                        locked_locks.append((cd, lock))
                    else:
                        # if one fails, roll back the successful ones
                        raise _LockFailedError()
        except Exception, e:
            # Roll back the locks
            for cd, lock in reversed(locked_locks):
                with self.redis.temp_connection(cd):
                    lock.release()

            # if we're just a failed lock, return false
            if isinstance(e, _LockFailedError):
                return False
            # otherwise, reraise the exception
            else:
                raise


        return True

    def release(self):
        for cd, lock in reversed(self.locks):
            with self.redis.temp_connection(cd):
                lock.release()

    def __enter__(self):
        return self.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
                
    def _make_lock(self, connection_dict):
        with self.redis.temp_connection(connection_dict):
            # seed the name with the connection info so we don't have to worry about replication
            seed = ','.join("%s:%s" % kv for kv in sorted(connection_dict.items()))
            seeded_name = "%s!%s" % (self.name, seed)
            print "making lock", seeded_name
            return self.redis.lock(seeded_name, self.timeout, self.sleep)


def main():

    servers = [
        dict(host='ubuntu1.local', port=6379, db=0),
        dict(host='ubuntu2.local', port=6379, db=0),
    ]

    r = MultiLockRedis(servers)
    
    while True:
        r._determine_master()
        time.sleep(1.0)



if __name__ == "__main__":
    main()
