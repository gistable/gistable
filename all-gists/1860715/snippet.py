#!/usr/bin/env python                                                           
import reddit, sys, time

def handle_ratelimit(func, *args, **kwargs):
    while True:
        try:
            func(*args, **kwargs)
            break
        except reddit.errors.RateLimitExceeded as error:
            print '\tSleeping for %d seconds' % error.sleep_time
            time.sleep(error.sleep_time)


def main():
    r = reddit.Reddit('PRAW loop test')
    r.login()

    last = None

    comm = r.get_subreddit('reddit_api_test')
    for i, sub in enumerate(comm.get_new_by_date()):
        handle_ratelimit(sub.add_comment, 'Test comment: %d' % i)
        cur = time.time()
        if not last:
            print '     %2d %s' % (i, sub.title)
        else:
            print '%.2f %2d %s' % (cur - last, i, sub.title)
        last = cur


if __name__ == '__main__':
    sys.exit(main())
