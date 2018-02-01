import redis
from redis import WatchError
import time

RATE = 0.1
DEFAULT = 100
TIMEOUT = 60 * 60

DEBUG = False

r = redis.Redis()


def token_bucket(tokens, key):
    """Return true or false bases on whether the tokens in bucket
    key can consumes amount tokens
    """
    pipe = r.pipeline()
    while 1:
        try:
            if DEBUG:
                print "\nUser tries to consume %s tokens\n" % str(tokens)
            # set a watch on available tokens and previous timestamp
            pipe.watch('%s:available' % key)
            pipe.watch('%s:ts' % key)

            current_ts = time.time()

            # get the current amount of tokens in the users bucket
            old_tokens = pipe.get('%s:available' % key)
            if DEBUG:
                print '\nUsers old tokens is %s\n' % str(old_tokens)
            if old_tokens is None:
                current_tokens = DEFAULT

            # else the user does have a value for tokens so we will increment them
            else:
                old_ts = pipe.get('%s:ts' % key)
                current_tokens = float(old_tokens) + min(
                    (current_ts - float(old_ts)) * RATE,
                    DEFAULT - float(old_tokens)
                )

            # now we do the actual consumption of tokens
            # and set the return value in the var consumes
            if 0 <= tokens <= current_tokens:
                current_tokens -= tokens
                consumes = True
            else:
                consumes = False
            if DEBUG:
                if consumes:
                    print '\nuser had enough tokens\n'
                else:
                    print '\nuser did not have enough tokensz\n'

            # put the pipeline back into buffered mode with MULTI
            pipe.multi()

            if DEBUG:
                print "\nUser now has %s\n" % str(current_tokens)

            # sets the new values in the users bucket
            pipe.set('%s:available' % key, current_tokens)
            pipe.expire('%s:available' % key, TIMEOUT)
            pipe.set('%s:ts' % key, current_ts)
            pipe.expire('%s:ts' % key, TIMEOUT)

            # execute the above set statements
            # raising a WatchError if the valuse have changed since we started
            pipe.execute()
            break
        except WatchError:
            # if there was a watch error lets just try again
            # ie. a watcherror means somebody modified the same bucket
            # before the start and end of the transaction
            continue
        finally:
            pipe.reset()
    # return whether the user had enough tokens or not
    return consumes


if __name__ == "__main__":
    tokens = 5
    key = '192.168.1.1'
    if token_bucket(tokens, key):
        print 'haz tokens'
    else:
        print 'cant haz tokens'
