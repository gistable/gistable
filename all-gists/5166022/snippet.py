"""
Python's set data structure is the only one without a literal
notation for an empty set.

http://excess.org/article/2012/11/python-container-literals/

This is an ast transformer to add an empty set notation with the
following form:

    empty_set = {_}

Usage:
At the top of your program,

    import EmptySetLiteral
    # Any module you import after this will have empty set notation.
    # It does not work for the current document!!!

"""
import ast
import imp
import sys
import os.path
import types


class EmptySetLiteralTransformer(ast.NodeTransformer):
    def visit_Set(self, node):
        try:
            if len(node.elts) == 1 and \
                isinstance(node.elts[0], ast.Name) and \
                    node.elts[0].id == "_":
                node.elts.pop()
        except:
            # If we ever get an exception, it's because this node
            # doesn't match the strict requirements of the literal {_}.
            # So we can return the node unmodified.
            pass
        return node


"""
The following section for hooking into python's import system is
shamelessly stolen from Fredrik Haard's Blaag.

http://blaag.haard.se/Using-the-AST-to-hack-constants-into-Python/
"""


def transform(src):
    """Transforms the given source and return the AST"""
    tree = ast.parse(src)
    cm = EmptySetLiteralTransformer()
    newtree = cm.visit(tree)
    return newtree


class Importer(object):
    """Importer to be put on meta_path to instrument any
    subsequent imports"""
    def __init__(self):
        self._cache = {}

    def find_module(self, name, path=None):
        try:
            suffix = name.split('.')[-1]
            self._cache[name] = imp.find_module(suffix)
        except ImportError:
            return None
        return self

    def load_module(self, name):
        """Load a module and instrument it. Will fallback to default
        behaviour if there is no source available, or if the module to
        be imported is not in (PY_SOURCE, PY_COMPILED, PY_DIRECTORY)"""

        module = types.ModuleType(name)  # create empty module object
        fd, pathname, (suffix, mode, type_) = self._cache[name]

        with fd:
            if type_ == imp.PY_SOURCE:
                filename = pathname
            elif type_ == imp.PY_COMPILED:
                filename = pathname[:-1]
            elif type_ == imp.PKG_DIRECTORY:
                filename = os.path.join(pathname, '__init__.py')
                module.__path__ = [pathname]
            else:
                return imp.load_module(name, fd, pathname,
                                       (suffix, mode, type_))
            if not filename == pathname:
                try:
                    with open(filename, 'U') as realfile:
                        src = realfile.read()
                except IOError:  # fallback
                    return imp.load_module(name, fd, pathname,
                                           (suffix, mode, type_))
            else:
                src = fd.read()

        module.__file__ = filename

        module = types.ModuleType(name)
        inlined = transform(src)
        code = compile(inlined, filename, 'exec')
        sys.modules[name] = module
        exec(code, module.__dict__)
        return module


def install_hook():
    """Install the import hook"""
    importer = Importer()
    sys.meta_path.insert(0, importer)

# Auto install the hook for imports
install_hook()
