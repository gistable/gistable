"""

    Tor IP checks

"""

import requests

from django.core.cache import cache

from celery import task

from conf import logs

logger = logs.get_logger()

# Content is like:
# 82.234.19.113
# 82.235.216.226
# 82.242.192.93
# 82.245.41.171
CSV_URL = "http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv"

# Memcached key used to store the list
CACHE_KEY = "tor-ip-exit-list"


def fetch_tor_ip_list():
    """ Stores Tor IP list to memcached

    :return: Set of IP addresses as string
    """

    r = requests.get(CSV_URL)
    results = []

    for row in r.content.split("\n"):
        row = row.strip()
        if not row:
            continue
        results.append(row)

    return frozenset(results)


def is_tor_ip(ip):
    """ Checks if ip address is a TOR exit node.

    Relies on periodically updated IP list.
    If IP list update has failed then gracefully assumes
    there are no Tor exit nodes. This is so that
    our service continues to function even if the external
    party we are relying on goes down.

    :param ip: IP address as a string
    """
    ips = cache.get(CACHE_KEY)

    if not ips:
        logger.warn("Tor IP list not available; IP check not active")
        return False

    return ip in ips


@task()
def update_ip_list():
    """ Background task to update the tor IP list.

    This is periodically configured to be run every 24 h.

    Results should be stord for longer period of time.
    """
    logger.info("Updating TOR exit node list from %s" % CSV_URL)
    ips = fetch_tor_ip_list()
    cache.set(CACHE_KEY, ips, 3600*24*3)
