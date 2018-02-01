from concurrent.futures import as_completed, ThreadPoolExecutor
from urllib.request import urlopen
import re
import sys


DEFAULT_REGEX = r'<input type="text" id="nacional" value="([^"]+)"/>'
CURRENCY = {
    'dolar': 'http://dolarhoje.com/',
    'euro': 'http://eurohoje.com/',
    'libra': 'http://librahoje.com/',
    'peso': 'http://pesohoje.com/'
}


def exchange_rate(url):
    response = urlopen(url).read().decode('utf-8')
    result = re.search(DEFAULT_REGEX, response)
    if result:
        return result.group(1)


def run_threads():
    with ThreadPoolExecutor(max_workers=len(CURRENCY)) as executor:
        waits = {
            executor.submit(exchange_rate, url): currency
            for currency, url in CURRENCY.items()
        }
        for future in as_completed(waits):
            currency = waits[future]
            print('{}: R${}'.format(currency, future.result()))


def run_serial():
    for currency, url in CURRENCY.items():
        print('{}: R${}'.format(currency, exchange_rate(url)))


if __name__ == '__main__':
    """
    To run serial
    $ python multi_requests.py
    To run multithread
    $ python multi_requests.py threads
    """
    if len(sys.argv) > 1 and sys.argv[1] == 'threads':
        run_threads()
    else:
        run_serial()