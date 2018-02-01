import argparse
import json

import falcon

from gunicorn.app.base import BaseApplication
from gunicorn.six import iteritems


class StandaloneApplication(BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict(
            [(key, value) for key, value in iteritems(self.options)
                if key in self.cfg.settings and value is not None]
        )
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def _get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='0.0.0.0')
    parser.add_argument('--port', '-p', default='8080')
    args = parser.parse_args()

    config = {
        'bind': '%s:%s' % (args.bind, args.port),
        'workers': 3,
    }
    return config


class ExampleResource:
    def on_get(self, req, resp):
        data = {'foo': 'bar'}
        resp.body = json.dumps(data)


def main():
    api = falcon.API()
    api.add_route('/', ExampleResource())

    config = _get_config()
    StandaloneApplication(api, config).run()


if __name__ == '__main__':
    main()
