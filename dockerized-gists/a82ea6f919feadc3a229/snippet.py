import os

import falcon
import jinja2


def load_template(name):
    path = os.path.join('templates', name)
    with open(os.path.abspath(path), 'r') as fp:
        return jinja2.Template(fp.read())


class ThingsResource(object):
    def on_get(self, req, resp):
        template = load_template('awesome.j2')

        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        resp.body = template.render(something='testing')

app = falcon.API()
things = ThingsResource()
app.add_route('/things', things)