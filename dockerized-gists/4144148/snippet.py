import argparse
import requests
import time


def _parse_args():
    parser = argparse.ArgumentParser(description='Zen out with github')

    # Github api limits 60/hour for unauthenticated requests
    parser.add_argument('--sleep', type=float, default=60.0, action='store',
                        dest='sleep_time', required=False,
                        help='Number of seconds to sleep between requests')
    parser.add_argument('--username', type=str, default=None, action='store',
                        dest='username', required=False,
                        help='Username to use for authentication')
    parser.add_argument('--password', type=str, default=None, action='store',
                        dest='password', required=False,
                        help='Password to use for authentication')

    return parser.parse_args()


def main():
    args = _parse_args()
    for zen in get_zen(args.sleep_time, args.username, args.password):
        print zen


def get_zen(sleep_time, username, password):
    """Infinite generator to keep looking for unique zen quotes from api"""

    zen_url = 'https://api.github.com/zen'
    zen_cache = []
    auth = (username, password) if None not in [username, password] else None

    while True:
        response = requests.get(zen_url, auth=auth)
        if not response.ok:
            print response.text
            raise StopIteration

        if response.text not in zen_cache:
            zen_cache.append(response.text)
            yield response.text

        time.sleep(sleep_time)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Script runs forever, so hide any stack traces for user quitting since
        # it's expected
        print
