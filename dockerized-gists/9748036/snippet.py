"""
setup:
    pip install requests
    pip install requests[socks]

super helpful:
    - http://packetforger.wordpress.com/2013/08/27/pythons-requests-module-with-socks-support-requesocks/
    - http://docs.python-requests.org/en/master/user/advanced/#proxies

"""
import requests


proxies = {
    'http': 'socks5://127.0.0.1:9150',
    'https': 'socks5://127.0.0.1:9150'
}


def main():
    url = 'http://ifconfig.me/ip'

    response = requests.get(url)
    print('ip: {}'.format(response.text.strip()))

    response = requests.get(url, proxies=proxies)
    print('tor ip: {}'.format(response.text.strip()))


if __name__ == '__main__':
    main()
