#!/usr/bin/python
# vim: fileencoding=utf-8
u'''Translate YAML written text to graphviz dot language

Input YAML text like below:

---
employee:
    - name
    - age
    - department ->
    - manager -> employee

department:
    - name
'''

from __future__ import print_function

import re
import yaml


class Item(list):
    def __init__(self, name, iterable=[]):
        self.name = name
        super(Item, self).__init__(iterable)

    def __repr__(self):
        return '<{0} {1}>'.format(self.name, super(Item, self).__repr__())

    def dot(self):
        '''return dot language representation of this object
        '''
        table = [
            u'<table bgcolor="#FAFAFA" border="0" cellborder="1"'
            u' cellspacing="0" cellpadding="4">',
            u'<tr><td align="center" bgcolor="#CCCCEE" port="f0">',
            escape(self.name),
            u'</td></tr>',
        ]
        arrows = []

        for i, v in enumerate(self, 1):
            mobj = re.match(r'^(.+)\s*->\s*(.+)?$', v, re.UNICODE)

            if mobj:
                v, arrow_to = mobj.groups()

                if arrow_to is None:
                    arrow_to = v

                v = v.strip()
                arrow_to = arrow_to.strip()

                arrows.append(u'"{name}":f{i} -> "{arrow_to}" []'.format(
                    name=escape(self.name), i=i, arrow_to=escape(arrow_to)))

            table.extend([
                u'<tr><td align="left" balign="left" port="f{}">'.format(i),
                br(escape(v)),
                u'</td></tr>',
            ])

        table.append(u'</table>')

        return u'\n'.join([
            u'{} ['.format(escape(self.name)),
            u'    label = <{}>'.format('\n'.join(table)),
            u']',
            u'\n'.join(arrows),
        ])


def quote(s):
    if not isinstance(s, basestring):
        s = str(s)
    return u'"%{}"'.format(s.replace(u'"', u'\\"'))


def escape(s):
    if isinstance(s, list):
        s = u',\n'.join(s)
    elif not isinstance(s, basestring):
        s = str(s)
    return s.replace(u'&', u'&amp;') \
            .replace(u'>', u'&gt;') \
            .replace(u'<', u'&lt;')


def br(s):
    if not isinstance(s, basestring):
        s = str(s)
    return s.replace(u'\n', u'<br />')


def yaml_to_dot(yml):
    items = [Item(name, contents) for name, contents in yaml.load(yml).items()]
    dots = [
        u'digraph g {',
        u'graph [',
        u'    rankdir = "LR"',
        u']',
        u'node [',
        # TODO: allow to customize fontsize
        u'    fontsize = "12"',
        u'    shape = "plaintext"',
        u']',
        u'',
    ]
    dots.extend(item.dot() for item in items)
    dots.append('}')

    return u'\n'.join(dots)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        input = open(sys.argv[1], 'r')

    else:
        input = sys.stdin

    print(yaml_to_dot(input).encode('utf-8'))
