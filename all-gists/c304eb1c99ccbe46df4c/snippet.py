from flask import Flask, request, session, g, redirect, url_for
from flask import abort, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

hosts = {
  'b': "https://code.google.com/p/android/issues/"
  's': "https://android.googlesource.com/",
  'r': "https://android-review.googlesource.com/",
  'g': "http://google.com/",
  #'m': "https://gmail.com",
  'm': "https://inbox.google.com/",
}

@app.route('/', defaults={'path': '/'})
@app.route('/<path:path>')
def go_path(path):
    host = request.host
    if ':' in host:
        host = host.split(':')[0]
    if host in hosts:
        target = hosts[host]
        if target.endswith('/'):
            target = target + request.full_path[1:]
        return redirect(target)
    abort(404)

def update_dnsmasq_conf():
    import os, platform
    FILENAME = '/var/cache/dnsmasq/dnsmasq.conf'
    try:
        os.makedirs(os.path.dirname(FILENAME))
    except OSError: pass

    with open(FILENAME, 'w') as f:
        #f.write('expand-hosts\n')
        f.write('localise-queries\n')
        node = platform.node()
        for host in hosts:
            # add alias hostname to local node
            f.write('cname=%s,%s\n'%(host, node))

    os.system('sudo systemctl restart dnsmasq')

if __name__ == '__main__':
    import os
    update_dnsmasq_conf()
    if os.getuid() == 0:
        app.run(host='0.0.0.0', port=80)
    else:
        app.run(host='0.0.0.0')