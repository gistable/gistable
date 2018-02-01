"""
This gist adds url expiration functionality to flask-webassets on App Engine.

Few hints how to use it:

- Disable updater: ASSETS_UPDATER = False.
- Use AppEngineBundle instead of standard webassets Bundle.
- Rebuild assets manually:
  * manage.py assets watch for development.
  * manage.py assets rebuild for deployment.
"""

import os

from webassets.bundle import Bundle

from app import app

try:
    from _webassets import files
except ImportError:
    files = {}


WEBASSETS_FILE = os.path.join(app.config['DIRNAME'], '_webassets.py')
WEBASSETS_TEMPLATE = "files = %(files)s"


class AppEngineBundle(Bundle):
    def _update_timestamp(self, env, filename):
        filepath = env.abspath(filename)
        last_modified = os.stat(filepath).st_mtime

        files[filename] = last_modified
        content = WEBASSETS_TEMPLATE % dict(files=repr(files))
        open(WEBASSETS_FILE, 'w+').write(content)

    def _make_url(self, env, filename, expire=True):
        last_modified = files.get(filename, 0)
        return env.absurl("%s?%d" % (filename, last_modified))

    def build(self, env=None, force=False):
        hunks = super(AppEngineBundle, self).build(env=env, force=force)
        env = self._get_env(env)
        self._update_timestamp(env, self.output)
        return hunks
