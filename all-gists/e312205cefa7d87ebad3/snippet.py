#!/usr/bin/python
from pandocfilters import toJSONFilter, RawInline, Para, Space, walk

def latex(s):
    return RawInline('latex', s)

def html(s):
    return RawInline('html', s)

def deindentParas(key, value, format, meta):
    # If we're here, then we are a child node of 
    # a noindent 'div.' 
    if key == 'Para':
        
        if format == 'latex':
            return Para([latex('\\noindent')]+ [Space()] + value)

        if format == 'html':
            return Para([html('<span class="noindent">')] + value + [html('</span>')])

    return

def noindent(key, value, format, meta):
    # Look at each div.
    if key == 'Div':
        [[ident, classes, kvs], contents] = value

        # If the Div is of the noindent class, we run deindentParas
        # on all of its children.
        if 'noindent' in classes:
           return walk(contents, deindentParas, format, meta)

    return 

if __name__ == "__main__":
  toJSONFilter(noindent)
