# the idea was come from https://gist.github.com/jvanasco/1616707

import types

def _var_dump(variable, depth = 0, not_new_line = False):
    padding = " " * 4 * depth
    key_padding = " " * 4 * (depth+1)
    first_padding = '' if not_new_line else padding
    not_new_line = True
    depth+= 1
    if type(variable) == types.DictType :
        items = []
        for key in variable :
            item = key_padding + "'%s' : %s" % (key,_var_dump(variable[key],depth, True))
            items.append(item)
        items = ',\n'.join(items)
        return '%s<Dictionary> {\n%s\n%s}' % ( first_padding, items, padding)
    elif type(variable) == types.ListType :
        items = []
        for item in variable :
            items.append(_var_dump(item, depth))
        items = ',\n'.join(items)
        return '%s<List> [\n%s\n%s]' % ( first_padding, items, padding)
    elif type(variable) == types.TupleType :
        items = []
        for item in variable :
            items.append(_var_dump(item, depth))
        items = ',\n'.join(items)
        return '%s<Tuple> (\n%s\n%s)' % ( first_padding, items, padding)
    elif type(variable) == types.InstanceType:
        items = []
        for key in dir(variable):
            item = key_padding + "%s : %s" % (key,_var_dump(getattr(variable,key),depth, True))
            items.append(item)
        items = ',\n'.join(items)
        return '%s<Instance of %s> (\n%s\n%s)' % ( first_padding, variable.__class__, items, padding)
    elif type(variable) == types.MethodType:
        return first_padding + '<Method>'
    elif type(variable) == types.FunctionType:
        return first_padding + '<Function>'
    elif type(variable) == types.StringType:
        return first_padding + "<String> '%s'" % variable
    elif type(variable) == types.IntType:
        return first_padding + "<Integer> %s" % variable
    elif type(variable) == types.LongType:
        return first_padding + "<Long> %s" % variable
    elif type(variable) == types.FloatType:
        return first_padding + "<Float> %s" % variable
    elif type(variable) == types.BooleanType:
        return first_padding + "<Boolean> %s" % variable
    elif type(variable) == types.NoneType:
        return first_padding + "<None>"
    else:
        return first_padding + "%s %s" % (type(variable), variable)

def var_dump(variable, **kwargs):
    show    = kwargs.pop('show', False)
    as_html = kwargs.pop('as_html', False)
    result  = _var_dump(variable)
    if as_html:
        result = '<pre>' + result.replace('<','&lt;').replace('>','&gt;') + '</pre>'
    if show:
        print(result)
    return result

# FAQ : Why the hell you need var_dump in Python?
if __name__ == '__main__':

    # Let's say I have a dictionary which one of its value contains an instance of a class
    class Human:
        def __init__(self):
            self.name = 'Clark'
            self.age = 15
            self.hobby = ['flying', 'kicking bastards']
        def fly(self):
            print('up up and away')
    data = {'name' : 'clark', 'object' : Human()}

    # use print
    print(data)
    # print will give you this:
    # {'object': <__main__.Human instance at 0xb724f3ec>, 'name': 'clark'}

    # use pprint
    import pprint
    pprint.pprint(data)
    # pprint will give you this:
    # {'name': 'clark', 'object': <__main__.Human instance at 0xb724f3ec>}

    # use var_dump
    var_dump(data, show=True)
    # var_dump will give you this:
    # <Dictionary> {
    #     'object' : <Instance of __main__.Human> (
    #         __doc__ : <None>,
    #         __init__ : <Method>,
    #         __module__ : <String> '__main__',
    #         age : <Integer> 15,
    #        fly : <Method>,
    #         hobby : <List> [
    #             <String> 'flying',
    #             <String> 'kicking bastards'
    #         ],
    #         name : <String> 'Clark'
    #     ),
    #     'name' : <String> 'clark'
    # }
