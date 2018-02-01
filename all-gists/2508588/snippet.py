from directoryhash import path_checksum
from functools import partial

def static(filename, _external=False):
    path = partial(url_for, 'static', filename=filename, _external=_external)
    host = app.config.get('CDN_HOSTNAME')
    if host:
      return u'http://{host}/{fingerprint}{path}'.format(
        host=host, fingerprint=g.fingerprint, path=path())
    return path(fingerprint=g.fingerprint)

@app.context_processor
def context():
    return dict(
        static=static
    )

@app.before_request
def set_fingerprint():
    g.fingerprint = redis.get('myapp:fingerprint') \
        or path_checksum([app.static_folder])

# TEMPLATE

<script src="{{ static("javascripts/app.js") }}"></script>