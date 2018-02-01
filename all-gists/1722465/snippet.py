# -*- coding: utf-8 -*-
import os
from optparse import make_option

import polib

from django.core.management import CommandError
from django.core.management.base import AppCommand


class Command(AppCommand):
    option_list = AppCommand.option_list + (
        make_option('-s', '--source',
            action='store',
            dest='from_app',
            default=False,
            help='Source app'),
        make_option('-l', '--language',
            action='store',
            dest='lang',
            default=False,
            help='Source app'),
        make_option('-f', '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force overwrite'),
    )

    def handle_app(self, app, **options):
        from django.db import models
        from_app = options.get('from_app')
        if not from_app:
            raise CommandError('please supply a source app')
        try:
            from_app = models.get_app(from_app)
        except IndexError:
            raise CommandError('%s is not a valid Django app' % from_app)

        _, source_dict = self.po(from_app, options.get('lang'))
        target, target_dict = self.po(app, options.get('lang'))

        for msgid, source_entry in source_dict.iteritems():
            if msgid not in target_dict:
                continue
            entry = target_dict[msgid]
            if not entry.msgstr or options.get('force'):
                entry.msgstr = source_entry.msgstr

        target.save(self.app_to_po_file(app, options.get('lang')))

    def po(self, app, language):
        pofile = self.app_to_po_file(app,language)
        po = polib.pofile(pofile)
        po_dict = dict((entry.msgid, entry) for entry in po)
        return po, po_dict

    def app_to_po_file(self, app, language):
        return os.path.join(os.path.dirname(app.__file__), 'locale', language, 'LC_MESSAGES', 'django.po')
