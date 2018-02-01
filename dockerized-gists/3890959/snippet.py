'''A function to refresh a lock that can timeout, before it times out.'''

def refresh_lock(conn, lockname, identifier, lock_timeout=10):
    pipe = conn.pipeline(True)
    lockname = 'lock:' + lockname

    while True:
        try:
            pipe.watch(lockname)
            if pipe.get(lockname) == identifier:
                pipe.multi()
                pipe.expire(lockname, lock_timeout)
                pipe.execute()
                return True

            pipe.unwatch()
            break

        except redis.exceptions.WatchError:
            pass

    return False
