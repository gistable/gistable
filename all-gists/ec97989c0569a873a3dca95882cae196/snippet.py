#!/bin/python

# This simple Python script runs simulations for different retry algorithms
# The results are printed as CSV data to the console
# See this article on my blog for details:
# https://blog.miguelgrinberg.com/post/how-to-retry-with-class

from random import random, choice


def fixed_retry(previous_sleep):
    # retry every second
    return 1


def exponential_backoff(previous_sleep):
    # start with one second, double with each additional attempt
    if previous_sleep == 0:
        return 1
    return previous_sleep * 2


def jitter1(sleep):
    # add up to 25% random time to sleep time
    return sleep * (1 + random() / 4)


def jitter2(sleep):
    # randomize the full sleep time
    return sleep * random()


def simulate_failure(retry_func, sleep_adjust_func=None,
                     requests_per_second=100, max_requests_per_second=200,
                     failure_length=10, simulate_from=-2, simulate_to=30):
    requests = []
    time = simulate_from
    rps = 0

    def fail_request(req):
        sleep_amount = req['sleep']
        if sleep_adjust_func:
            sleep_amount = sleep_adjust_func(sleep_amount)
        if req['time'] <= time:
            req['time'] += sleep_amount
            req['sleep'] = retry_func(req['sleep'])

    print("time,ok,failed")
    while time < simulate_to:
        service_is_down = time >= 0 and time < failure_length

        # new requests added in this slot
        new = requests_per_second

        # count how many outstanding requests retry in this time slot
        retries = len([req for req in requests if req['time'] <= time])

        # add new requests
        for i in range(new):
            requests.append({'time': time - random(), 'sleep': retry_func(0)})

        if service_is_down:
            num_ok = 0
        else:
            num_ok = new + retries \
                if new + retries < max_requests_per_second \
                else max_requests_per_second
        print('{},{},{}'.format(time, num_ok, new + retries - num_ok))


        # update outstanding requests
        if service_is_down:
            # requests are failing in this time slot
            # any requests that run in this time slot need to be retried later
            for req in requests:
                fail_request(req)
        else:
            # requests are succeeding in this time slot, so we remove as many
            # as we have capacity for
            finished_requests = [req for req in requests
                                 if req['time'] <= time]
            requests = [req for req in requests if req['time'] > time]
            while len(finished_requests) > max_requests_per_second:
                req = choice(finished_requests)
                finished_requests.remove(req)
                fail_request(req)
                requests.append(req)

        time += 1


print("# Retries at fixed intervals")
simulate_failure(fixed_retry)
print("# Retries with exponential backoff")
simulate_failure(exponential_backoff)
print("# Retries with exponential backoff and 25% jitter")
simulate_failure(exponential_backoff, jitter1)
print("# Retries with exponential backoff and full jitter")
simulate_failure(exponential_backoff, jitter2)