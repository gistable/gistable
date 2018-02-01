    ret = is_rate_okay(keys=[rate_key],
              args=[call_count, max_cps])

    if ret is None:
        plivo_call.retry(countdown=randint(60,120))
        return False