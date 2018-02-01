import sys
import ast

is_if = lambda s: isinstance(s, ast.If)
is_for = lambda s: isinstance(s, ast.For)
is_call = lambda s: isinstance(s, ast.Call)
call_name_is = lambda s, n: is_call(s) and hasattr(s.func, 'attr') and s.func.attr == n
has_else = lambda s: is_if(s) and len(s.orelse) > 0
is_return = lambda s: isinstance(s, ast.Return)
is_name = lambda s: isinstance(s, ast.Name)
is_boolean = lambda n: is_name(n) and n.id in ('True', 'False')

def find_for_x_in_y_keys(tree):
    """
    >>> code = '''for x in y.keys():
    ...     pass
    ... '''
    >>> tree = ast.parse(code)
    >>> assert find_for_x_in_y_keys(tree) == [1]

    >>> code = '''for x in y:
    ...     pass
    ... '''
    >>> tree = ast.parse(code)
    >>> assert find_for_x_in_y_keys(tree) == []
    """
    found = []

    for node in ast.walk(tree):
        checks = is_for(node) \
                 and call_name_is(node.iter, 'keys')

        if checks:
            found.append(node.lineno)

    return found


def find_if_x_ret_bool_else_ret_bool(tree):
    """
    >>> code = '''if foo:
    ...     print True
    ... '''
    >>> tree = ast.parse(code)
    >>> assert find_if_x_ret_bool_else_ret_bool(tree) == []

    >>> code = '''if foo:
    ...     return False
    ... else:
    ...     return True
    ... '''
    >>> tree = ast.parse(code)
    >>> assert find_if_x_ret_bool_else_ret_bool(tree) == [1]
    """
    found = []

    for node in ast.walk(tree):
        checks = is_if(node) \
                 and is_return(node.body[0]) \
                 and is_boolean(node.body[0].value) \
                 and has_else(node) \
                 and is_return(node.orelse[0])\
                 and is_boolean(node.orelse[0].value)

        if checks:
            found.append(node.lineno)

    return found

def lookup_paths_for_file(code_file, ast_paths):
    try:
        tree = ast.parse(open(code_file).read())
    except: # Catch all, don't care.
        print "Error: Could not parse: {}".format(code_file)
        return

    for friendly, checker in ast_paths.items():
        adherance = checker(tree)
        for lineno in adherance:
            print '{}: {}: {}'.format(
                    code_file,
                    friendly,
                    lineno)

if __name__ == '__main__':
    AST_PATHS = {
        'If/RetBool/Else/RetBool': find_if_x_ret_bool_else_ret_bool,
        'For/In/DictKeys': find_for_x_in_y_keys
    }
    
    lookup_paths_for_file(sys.argv[1], AST_PATHS)


