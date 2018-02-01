#!/usr/bin/env python

import os
import web
from jinja2 import Environment,FileSystemLoader

# Router
urls = (
    "/.*", "hello",
    '/contact', 'rsvp'
)

app = web.application(urls, globals())

# Define template rendering with jinja2 without overriding native render
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    return jinja_env.get_template(template_name).render(context)

# Controller
class hello:
    def GET(self):
        return render_template('index.html')

class rsvp:
    def GET(self):
        pass

if __name__ == "__main__":
    app.run()