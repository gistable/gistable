#!/usr/bin/python
# vim: fileencoding=utf-8


u'''Translate YAML written text to graphviz dot language

Input YAML text like below:

---
foo:
  - bar
  - baz:
    - hello:
      - world
  - lorum
---

Reference: https://gist.github.com/nakamuray/7653403
Author: Richard Caceres, richard@archive.org
Usage: python yaml2dot-tree.py test.yaml > output.gv 
'''


import yaml


def quote(s):
    if not isinstance(s, basestring):
        s = str(s)
    return u'"{}"'.format(s.replace(u'"', u'\\"'))


def edge_str(a, b=None):
    if b is not None:
        return '%s -> %s' % (quote(a), quote(b))
    else:
        return '%s' % quote(a)


def get_edges(name, children):
    edges = []
    edges.append(edge_str(name))
    for c in children:
        if isinstance(c, basestring):
            edges.append(edge_str(name, c))
        elif isinstance(c, dict):
            key = c.keys()[0]
            edges.append(edge_str(name, key))
            edges = edges + get_edges(key, c[key])
    return edges

def yaml_to_dot(yml):
    edges = []
    for name, children in yaml.load(yml).items():
        edges = edges + get_edges(name, children)

    tmpl = """digraph {
node [shape=rectangle];
rankdir=LR;
splines=false;
    %s
}
    """
    gv = tmpl % ";\n    ".join(edges)
    return gv



if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        input = open(sys.argv[1], 'r')
    else:
        input = sys.stdin
    print(yaml_to_dot(input).encode('utf-8'))