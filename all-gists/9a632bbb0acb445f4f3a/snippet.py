# -*- coding: utf-8 -*-

import os
import sys

from flask.ext.script import Command, Option


class GunicornServer(Command):
    """Run the app within Gunicorn"""

    def get_options(self):
        from gunicorn.config import make_settings

        settings = make_settings()
        options = (
            Option(*klass.cli, action=klass.action)
            for setting, klass in settings.iteritems() if klass.cli
        )
        return options

    def run(self, *args, **kwargs):
        run_args = sys.argv[2:]
        run_args.append('manage:app')
        os.execvp('gunicorn', [''] + run_args)