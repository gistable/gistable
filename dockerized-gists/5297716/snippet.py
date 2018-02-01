# vim: fileencoding=utf-8 :

import logging

import eventlet

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

SERVER_ADDR = ('0.0.0.0', 843)
POLICY_FILE = u"""<?xml version="1.0"?>
<!DOCTYPE cross-domain-policy SYSTEM "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd">
<cross-domain-policy>
  <allow-access-from domain="*" to-ports="32123"/>
</cross-domain-policy>
\x00"""


def handle(client, addr):
    logging.info('connected: %s:%s' % addr)
    client.sendall(POLICY_FILE)
    client.close()

def main():
    server = eventlet.listen(SERVER_ADDR)
    pool = eventlet.GreenPool(10000)
    try:
        while True:
            client, addr = server.accept()
            pool.spawn_n(handle, client, addr)
    except KeyboardInterrupt, e:
        pass

if __name__ == '__main__':
    main()
