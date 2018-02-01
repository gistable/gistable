"""
Transforms a normal Python file to pep484 annotations using Jedi.

Usage:
    pep484transform.py <file> [-d]

Options:
    -d, --debug  Show Jedi's debug output.
"""
from os.path import abspath
from itertools import chain
import jedi
from jedi.evaluate.finder import _eval_param


def transform(file_name, debug=False):
    """
    Takes a file name returns the transformed text.
    """
    if debug:
        jedi.set_debug_function()

    names = jedi.names(path=file_name, all_scopes=True)
    param_names = [p for p in names if p.type == 'param']
    for param in param_names:
        # This is all very complicated and basically should just be replaced
        # with param.goto_definition(), once that api is being added (it's
        # planned).
        e = param._evaluator
        jedi_obj = param._definition
        types = _eval_param(e, jedi_obj, jedi_obj.get_parent_scope())

        if types and param.name != 'self':
            # Now refactor, Jedi has a round-trippable parser, yay!
            annotation = types_to_string(types, abspath(file_name))
            jedi_obj.name.value += ': ' + annotation

    # Get the module and generate the code.
    return jedi_obj.get_parent_until().get_code()


def types_to_string(types, path):
    transformed = set(type_to_string(typ, path) for typ in types)
    if len(transformed) == 1:
        return list(transformed)[0]
    else:
        # If wanted we could filter other modules with:
        # if typ.get_parent_until().path == path
        s = ', '.join(transformed)
        return 'Union[%s]' % s


def type_to_string(typ, path):
    name = str(typ.name)
    # Possibility to do various transformations, here's one for list and set.
    if str(typ.get_parent_until().name) == 'builtins':
        if name == 'NoneType':
            name = 'None'
        elif name in ('list', 'set'):
            types = list(chain.from_iterable(typ.py__iter__()))
            # If no types are available, don't transform to e.g. List[int], just
            # use list.
            if types:
                # Recurse!
                s = types_to_string(types, path)
                name = '%s%s[%s]' % (name[0].upper(), name[1:], s)
    return name


if __name__ == '__main__':
    import docopt

    result = docopt.docopt(__doc__)
    print(transform(result['<file>'], result['--debug']))
