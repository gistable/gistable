# coding:utf-8

from sys import modules
import gc
import inspect

import six

from django.core.management.base import BaseCommand
from django.dispatch.dispatcher import Signal, WeakMethod


FORMATS = {
    'vim': '{path}:{line}:{name}',
    'human': '{name} in line {line} of {path}',
}

class Command(BaseCommand):
    help = 'Show all signals receivers'
    def add_arguments(self, parser):
        parser.add_argument('--line_format', choices=FORMATS.keys(), default='human',
                help='Line format (available choices: {0})'.format(', '.join(FORMATS))
                )
    def handle(self, *args, **options):
        line_format = options['line_format']
        if line_format not in FORMATS:
            raise CommandError('format must be on of {0}, not {1}'.format(line_format, FORMATS.keys()))
        msg = FORMATS[line_format]
        signals = [obj for obj in gc.get_objects() if isinstance(obj, Signal)]
        for signal in signals:
            for receiver in signal.receivers:
                _, receiver = receiver
                func = receiver()
                name = func.__qualname__ if six.PY3 else func.__name__
                print(msg.format(name=name, line=inspect.getsourcelines(func)[1], path=inspect.getsourcefile(func)))
