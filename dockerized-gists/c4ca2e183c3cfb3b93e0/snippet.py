#!/usr/bin/python
# -*- coding: utf-8 -*-

import posixpath
from jinja2 import Environment, FileSystemLoader
from tornado.template import BaseLoader


class Template(object):
    def __init__(self, template):
        self.template = template

    def generate(self, **kwargs):
        return self.template.render(**kwargs)


class JinjaLoader(BaseLoader):
    def __init__(self, root_directory, **kwargs):
        # 为父类的 init 传空
        super(JinjaLoader, self).__init__()
        _kwargs = {
            "loader": FileSystemLoader(root_directory),
        }
        _kwargs.update(kwargs)
        self.env = Environment(**_kwargs)

    def resolve_path(self, name, parent_path=None):
        if parent_path and not parent_path.startswith("<") and \
                not parent_path.startswith("/") and \
                not name.startswith("/"):
            file_dir = posixpath.dirname(parent_path)
            name = posixpath.normpath(posixpath.join(file_dir, name))
        return name

    def _create_template(self, name):
        return Template(self.env.get_template(name))
