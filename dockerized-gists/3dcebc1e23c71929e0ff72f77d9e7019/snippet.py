# Replace ``netstat -rn | grep "^0.0.0.0 " | cut -d " " -f10`` with direct parsing of /proc/net/route
def get_default_gateway_linux():
    """Read the default gateway directly from /proc."""
    import socket, struct
    with open("/proc/net/route") as f:
        for line in f:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("=L", int(fields[2], 16)))


def get_tor_proxy():
    hardware_node = get_default_gateway_linux() if os.path.exists('/vagrant') else '127.0.0.1'
    proxy = 'socks5://%s:9150' % hardware_node
    return {
        'http': proxy,
        'https': proxy
    }


def new_tor_id():
    from tratatype.utils.TorCtl import TorCtl
    conn = TorCtl.connect(controlAddr=get_default_gateway_linux() if os.path.exists('/vagrant') else '127.0.0.1', controlPort=9151, passphrase="")
    conn.send_signal("NEWNYM")
    print "new tor identity"
    
    
def fetch(urls, db, delay=0, proxies=None, callback=None):
    session = requesocks.session()

    if proxies is not None:
        session.proxies = proxies

    for url in urls:
        print url

        if db is not None:
            already = db.get('select * from pages where url = "%(url)s" and status_code in (200, 404)' % {'url': url})
            if already:
                print 'skipping %s' % url
                continue

        r = session.get(url)
        if callback is not None:
            callback(db, url, r)
        if proxies and (r.status_code not in (200, 404) or random.uniform(0, 8) < 1):
            new_tor_id()
        if delay:
            time.sleep(random.uniform(0, delay))

        print '%s %s' % (r.status_code, r.url)