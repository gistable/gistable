import sys
import logging
from pyramid.compat import configparser
from pyramid.util import DottedNameResolver
from pyramid.paster import bootstrap

# pshellintellij uses first two arguments as ports to connect shell
if len(sys.argv) > 3:
    config_file = sys.argv[3]
else:
    config_file = 'development.ini'

bootstrap = (bootstrap,)
config = configparser.ConfigParser()
config.read(config_file)

resolver = DottedNameResolver(None)
loaded_objects = {}
object_help = {}
setup = None

try:
    items = config.items('pshell')
    for k, v in items:
        if k == 'setup':
            setup = v
        else:
            loaded_objects[k] = resolver.maybe_resolve(v)
            object_help[k] = v
except configparser.NoSectionError:
    pass

# use #main section by default
config_uri = config_file

# bootstrap the environ
env = bootstrap[0](config_uri)

# remove the closer from the env
closer = env.pop('closer')

# setup help text for default environment
env_help = dict(env)
env_help['app'] = 'The WSGI application.'
env_help['root'] = 'Root of the default resource tree.'
env_help['registry'] = 'Active Pyramid registry.'
env_help['request'] = 'Active request object.'
env_help['root_factory'] = (
    'Default root factory used to create `root`.')

if setup:
    # store the env before muddling it with the script
    orig_env = env.copy()
    # call the setup callable
    resolver = DottedNameResolver(None)
    setup = resolver.maybe_resolve(setup)
    setup(env)
    # remove any objects from default help that were overridden
    for k, v in env.items():
        if k not in orig_env or env[k] != orig_env[k]:
            env_help[k] = v

# load the pshell section of the ini file
env.update(loaded_objects)

# eliminate duplicates from env, allowing custom vars to override
for k in loaded_objects:
    if k in env_help:
        del env_help[k]

locals().update(env)

# log sqlalchemy queries
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# generate help text
help = ''
if env_help:
    help += 'Environment:'
    for var in sorted(env_help.keys()):
        help += '\n  %-12s %s' % (var, env_help[var])
if object_help:
    help += '\n\nCustom Variables:'
    for var in sorted(object_help.keys()):
        help += '\n  %-12s %s' % (var, object_help[var])
print(help)
del env_help, help, resolver, closer, loaded_objects, object_help, setup, bootstrap
