#encoding: utf-8
import uno

def open_document(url):
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    context = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
    document = desktop.loadComponentFromURL(url, "_blank", 0, ())
    return document

def iter_elements(elem):
    enum = elem.createEnumeration()
    while enum.hasMoreElements():
        yield enum.nextElement()

def nonempty_elements(elem):
    return (el for el in iter_elements(elem) if hasattr(el, 'getString') and el.getString())

def list_elements(elem):
    return list(iter_elements(elem))

def print_elements(elem):
    for el in iter_elements(elem):
        print el.getString()

def is_leaf(elem):
    return not hasattr(elem, 'hasElements')

def is_bold(elem):
    if is_leaf(elem):
        return elem.CharWeight > 100
    else:
        return all(is_bold(el) for el in iter_elements(elem))

def is_italic(elem):
    if is_leaf(elem):
        return elem.CharPosture.value == 'ITALIC'
    else:
        return all(is_italic(el) for el in iter_elements(elem))

def is_underline(elem):
    if is_leaf(elem):
        return elem.CharUnderline == 1
    else:
        return all(is_underline(el) for el in iter_elements(elem))

def is_list(elem):
    return bool(elem.NumberingRules) and elem.NumberingRules.ElementType.typeClass.value == 'SEQUENCE'

def color(elem):
    code = elem.CharColor
    if code in [0, -1, -16777216]:
        return 'black'
    elif code == 255:
        return 'blue'
    elif code == 32768:
        return 'green'
    elif code == 16711680:
        return 'red'
    elif code == 16737792:
        return 'orange'
    else:
        raise Exception('Unknown color code %s for elem "%s"' % (code, elem.getString()))
