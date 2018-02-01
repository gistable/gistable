def pprint_defaultdict():
    from collections import defaultdict
    import IPython
    ip = get_ipython()
    tf = ip.display_formatter.formatters['text/plain']
    def _print_default_dict(arg, p, cycle):
        """ Pretty print a defaultdict. """
        def rec(obj, indent=0, level=0):
            if isinstance(obj, defaultdict) or isinstance(obj, dict):
                p.text('{\n')
                indent += 1
                l = len(obj)
                dotdotdot = False
                for idx, k in enumerate(sorted(obj, key=lambda k: k)):
                    v = obj[k]
                    if idx <= 4 or l-idx <= 5:
                        if (idx != 0) and not (l-idx == 5 and dotdotdot):
                            p.text(',\n')
                        p.text(' '*indent + IPython.lib.pretty.pretty(k))
                        p.text(':')
                        rec(v, indent, level+1)
                    elif not dotdotdot:
                        p.text('\n\n' + ' '*indent + '...\n\n')
                        dotdotdot = True
                indent -= 1
                p.text('\n' + ' '*indent + '}')
            else:
                p.text(IPython.lib.pretty.pretty(obj))
        rec(arg)
    tf.for_type(defaultdict, _print_default_dict)
    
pprint_defaultdict()