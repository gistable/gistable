# -*- coding: utf-8
"""\
A simple demo of logging configuration with YAML (Python 2.7)
=============================================================

Requires PyYAML -> "easy_install PyYAML"

See the recipes for configuring logging with dicts and YAML
- http://docs.python.org/2.7/howto/logging-cookbook.html
- http://stackoverflow.com/questions/10519392/python2-7-logging-configuration-with-yaml
"""

import logging
import logging.config
import yaml
import StringIO

# Should be a config file in real app

YAML_CONF = """\
%YAML 1.2
---
# Config  for my application
# --------------------------
myapp:
  foo: bar
  bar: [1, 2]

# Config for logging
# ------------------
# See http://docs.python.org/2.7/library/logging.config.html#configuration-dictionary-schema

logging:
  version: 1
  disable_existing_loggers: true

  # Configuring the default (root) logger is highly recommended

  root:
    level: !!python/name:logging.NOTSET
    handlers: [console]

  loggers:

    # Logging from my application

    myapp.lib:
      level: !!python/name:logging.WARN
      handlers: [logfile]
      qualname: myapp.lib
      propagate: false
    myapp.cli:
      level: !!python/name:logging.WARN
      handlers: [console]
      qualname: myapp.cli
      propagate: false

    # Controlling logging of 3rd party libs

    sqlalchemy.engine:
      level: !!python/name:logging.WARN
      handlers: [logfile]
      qualname: sqlalchemy.engine
      propagate: false
    sqlalchemy.pool:
      level: !!python/name:logging.WARN
      handlers: [logfile]
      qualname: sqlalchemy.pool
      propagate: false

  handlers:
    logfile:
      class: logging.FileHandler
      filename: sample.log
      formatter: simpleFormatter
      level: !!python/name:logging.NOTSET
    console:
      class: logging.StreamHandler
      stream: ext://sys.stdout
      formatter: simpleFormatter
      level: !!python/name:logging.NOTSET

  formatters:
    simpleFormatter:
      class: !!python/name:logging.Formatter
      format: '%(name)s %(asctime)s %(levelname)s %(message)s'
      datefmt: '%d/%m/%Y %H:%M:%S'
"""

# Loading config. Of course this is in another file in the real life

global_config = yaml.load(StringIO.StringIO(YAML_CONF))

# Configuring logging with the subset of the dict
#

logging.config.dictConfig(global_config['logging'])

# Using explicitely the root logger always logs to the console

logging.info("This is an info of the root logger")

# The unconfigured loggers are captured by the root logger (-> console)

unconfigured_logger = logging.getLogger('unconfigured')
unconfigured_logger.info("This is an info from an unknown / unconfigured source")

# Logging from myapp.cli

myapp_cli_logger = logging.getLogger('myapp.cli')
myapp_cli_logger.info("This is an info from myapp.cli")  # Not recorded
myapp_cli_logger.warning("This is a warning from myapp.cli")  # -> console

# Logging from myapp.lib

myapp_lib_logger = logging.getLogger('myapp.lib')
myapp_lib_logger.info("This is an info from myapp.lib")  # Not recorded
myapp_lib_logger.warning("This is a warning from myapp.lib")  # -> sample.log

# Controlling logs from 3rd party libs

sqla_logger = logging.getLogger('sqlalchemy.engine')
sqla_logger.info("This is an info from SQLAlchemy")  # Not recorded
sqla_logger.warning("This is a warning from SQLAlchemy")  # -> sample.log

print "Now look at the file 'sample.log'"
