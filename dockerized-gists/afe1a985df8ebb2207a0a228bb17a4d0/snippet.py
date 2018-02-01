from redis import Redis
import time
redis = Redis()


def work_from_queue(queue):

    while True:
        res = redis.rpop(queue)

        if res:
            yield res.decode('utf-8')
        else:
            time.sleep(0.1)
