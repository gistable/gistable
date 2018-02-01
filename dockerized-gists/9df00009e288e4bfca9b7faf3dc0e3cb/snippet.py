#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division


import sys
import argparse
import ast
import io


def print8(*args, **kwargs):
    if "file" in kwargs:
        dest = kwargs["file"]
    else:
        dest = sys.stdout
    print(b" ".join(unicode(x).encode("utf-8") for x in args), file=dest)


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Verbose output.")
    p.add_argument("sources", nargs="+")
    args = p.parse_args([x.decode("utf-8") for x in argv[1:]])
    
    for filename in args.sources:
        with io.open(filename, mode="rb") as f:
            tree = ast.parse(f.read())
    
        #tree = ast.parse("a = u'us'\nb = 'bs'")
    
        def str_node(node):
            if isinstance(node, ast.AST):
                fields = [(name, str_node(val)) for name, val in ast.iter_fields(node) if name not in ("left", "right")]
                rv = "%s(%s" % (node.__class__.__name__, ", ".join("%s=%s" % field for field in fields))
                return rv + ")"
            else:
                return repr(node)
    
        def ast_visit(node, level=0):
            if node.__class__.__name__ == "Str":
                if hasattr(node, "lineno"):
                    fields = dict(ast.iter_fields(node))
                    if "s" in fields:
                        if isinstance(fields["s"], str):
                            print8("%s:%d: %s" % (filename, node.lineno, repr(fields["s"])))
            #print("  " * level + str_node(node))
            for field, value in ast.iter_fields(node):
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, ast.AST):
                            ast_visit(item, level=level+1)
                elif isinstance(value, ast.AST):
                    ast_visit(value, level=level+1)
    
        ast_visit(tree)
    
    return 0
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
