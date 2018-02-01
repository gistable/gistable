# -*- coding: utf-8 -*-
"""
    printr is a module that allows to emulate the print_r() function of PHP by
    printing the objects properties of a class instance and its internal
    structure

    Use:
        You must get an object of a class instance and then, you can call to
        the printr function

    Example:
        from printr import printr
        myobject = MyClass()
        printr(myobject)

    Documentation:
        Please, visit the www.python-printr.org Web site for more about
        Python-printr :)

    Developed by Eugenia Bahit (www.eugeniabahit.com)
    Under a GPL 3.0 licence

    Thanks to:
        Mariano Garcia Berrotaran
            by his idea about using "obj.__class__.__name__" at the
            get_human_object_name function :)
"""

IDENTATION_CHAR = " "
TAB_WIDTH = 4


def get_human_object_name(obj, is_collection=False):
    """
    Convert an object type in a human readable string
    """
    aditional = ' collection' if is_collection else ''
    return "<%s object%s>" % (obj.__class__.__name__, aditional)


def get_human_value(value):
    """
    Convert an object value in a human readable string
    """

    if str(value) == '':
        return "''"
    elif str(value).startswith('<'):
        return get_human_object_name(value)
    elif isinstance(value, list):
        if str(value[0]).startswith('<'):
            return get_human_object_name(value[0], True)
        else:
            return value
    else:
        return value


def printr(obj, tabs=TAB_WIDTH):
    """
    Print the object properties recursively in a human readable mode
    """

    if tabs == TAB_WIDTH:
        print get_human_object_name(obj)

    ident = IDENTATION_CHAR * tabs
    spaces = IDENTATION_CHAR * (tabs + TAB_WIDTH)

    print "%s{" % ident

    for prop, value in vars(obj).iteritems():
        print "%s%s: %s" % (spaces, prop, get_human_value(value))

        if str(value).startswith('<') and str(value).endswith('>'):
            printr(value, (tabs + TAB_WIDTH))
        elif isinstance(value, list):
            if str(value[0]).startswith('<'):
                for elemento in value:
                    printr(elemento, (tabs + TAB_WIDTH))

    print "%s}" % ident
