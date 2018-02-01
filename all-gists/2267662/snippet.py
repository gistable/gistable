import ast

app = lambda name, *args: \
        ast.Call(
            func=ast.Name(id=name, ctx=ast.Load(), lineno=0, col_offset=0),
            args=list(args), keywords=[], vararg=None,
            lineno=0, col_offset=0)


abs = lambda arg, body: \
        ast.Lambda(
            args=ast.arguments(args=[arg], defaults=[]),
            body=body, lineno=0, col_offset=0)

arg = lambda id: ast.Name(id=id, ctx=ast.Param(), lineno=0, col_offset=0)


class MonadTransformer(ast.NodeTransformer):
    def visit_ListComp(self, node):
        return self.modify(
            rewrite(node.elt),
            [rewrite(generator) for generator in node.generators])

    @staticmethod
    def modify(elt, generators):
        # Rewrite rules:
        # [e] => __return__(e)
        # [e for e in (etc)] => __bind__(e, lambda p: [e (etc)])
        # (or something along those lines :-D)

        elt = app('__return__', elt)

        for generator in reversed(generators):
            if generator.ifs:
                raise NotImplementedError

            elt = app(
                '__bind__', generator.iter,
                abs(arg(generator.target.id), elt))

        return elt


def rewrite(ast_):
    return MonadTransformer().visit(ast_)

def main():
    code = '''

def f(l):
    return [a * 2 for a in l]
'''

    ast_ = compile(code, '<string>', 'exec', ast.PyCF_ONLY_AST)
    new = rewrite(ast_)
    ctx = compile(new, '<string>', 'exec')

    LIST_MONAD = {
        '__return__': lambda v: [v],
        '__bind__': lambda m, f: [z for l in m for z in f(l)],
    }

    list_local = {}
    exec ctx in LIST_MONAD, list_local

    fl = list_local['f']
    print 'fl([1, 2, 3] =', fl([1, 2, 3])
    print 'fl([]) =', fl([])

    MAYBE_MONAD = {
        '__return__': lambda v: v,
        '__bind__': lambda m, f: f(m) if m is not None else None,
    }

    maybe_local = {}
    exec ctx in MAYBE_MONAD, maybe_local

    fm = maybe_local['f']
    print 'f(123) =', fm(123)
    print 'f(None) =', fm(None)

main()