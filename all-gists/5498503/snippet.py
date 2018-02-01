import os
from fabric.api import *
from jinja2 import Environment, FileSystemLoader
from StringIO import StringIO

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

@task
def config():
    # put nginx.conf template into remote nginx folder

    if env.apps != []:
        put(os.path.join(PROJECT_PATH, 'templates', 'base_nginx.conf'),
            '/etc/nginx/nginx.conf', 
            use_sudo=True)
        for app in env.apps:
            if not env.websites[app].has_key('servername'):
                env.websites[app]['servername'] = env.websites[app]['hosts'][0]
            put(getAndRenderTemplate(
                    '%s_nginx.conf' % app,
                    {
                        'app': app,
                        'host': env.websites[app]['hosts'][0],
                        'port': env.websites[app]['port'],
                        'user': env.websites[app]['user'],
                        'servername': env.websites[app]['servername'],
                    }
                ), 
                '/etc/nginx/sites-enabled/%s_nginx.conf' % app, 
                use_sudo=True)

    sudo('nginx -t')

def getAndRenderTemplate(filename, nginxVars):
    jinja_env = Environment(loader=FileSystemLoader('templates'))
    tmpl = jinja_env.get_template(filename)
    return StringIO(tmpl.render(nginxVars))

