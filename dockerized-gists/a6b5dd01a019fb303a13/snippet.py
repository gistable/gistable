# -*- coding: utf-8 -*-
#
# Sphinx extension for renaming _static/ directory
#
# Author: Takeshi KOMIYA / License: BSD
#

import re
import os
import shutil


def on_builder_inited(app):
    if app.builder.name == 'html':
        replacer = lambda uri: re.sub('^_static/', app.config.staticdir_name, uri)
        app.builder.script_files = map(replacer, app.builder.script_files)
        app.builder.css_files = map(replacer, app.builder.css_files)


def on_html_page_context(app, pagename, templatename, context, doctree):
    original_pathto = context['pathto']

    def pathto(otheruri, *args, **kwargs):
        otheruri = re.sub('^_static/', app.config.staticdir_name, otheruri)
        return original_pathto(otheruri, *args, **kwargs)

    context['pathto'] = pathto


def on_build_finished(app, exception):
    if app.builder.name == 'html' and exception is None:
        staticdir = os.path.join(app.outdir, '_static')
        if os.path.exists(staticdir):
            new_staticdir = os.path.join(app.outdir, app.config.staticdir_name)
            shutil.move(staticdir, new_staticdir)


def setup(app):
    app.add_config_value('staticdir_name', '_my_static/', 'html')
    app.connect('builder-inited', on_builder_inited)
    app.connect('html-page-context', on_html_page_context)
    app.connect('build-finished', on_build_finished)
