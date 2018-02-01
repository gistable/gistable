import re
import execjs


def find_equations(string):
    """ Take in a string, and convert everything between $ ... $ into an inline
    equation and everything between $$ ... $$ into a centred equation. """

    doubledollar = re.compile(ur"\$\$([^$]+)\$\$")
    singledollar = re.compile(ur"(?<![\$])\$([^$]+)\$(?!\$)")

    inline_equations = re.findall(singledollar, string)
    centred_equations = re.findall(doubledollar, string)

    return inline_equations, centred_equations


def remove_dollars(string):
    """ Takes equation delimited by dollars as input, and removes the dollar
    signs at the beginning and end. """

    return re.sub("[\$]", "", string)


def import_katex():
    """ Imports katex into the local namespace for use as
    `katex.call("katex.renderToString", "E = mc^2") """

    source = open("lib/katex.js").read()
    katex = execjs.compile(source)

    return True


def eqn_to_html(eqn_string):
    """ Takes equation string, e.g. "E = mc^2", and outputs KaTeX HTML """

    try:
        return katex.call("katex.renderToString", "E = mc^2")
    except ReferenceError:
        print "Error rendering KaTeX HTML. Please ensure that you have",
        print "imported KaTeX into the Python namespace."
        return False


def replace_eqn(string):
    """ Takes a block of text, finds the equations and replaces the text with
    HTML code """

    pass


with open("katex_markdown.md") as f:
    original_content = f.read()

import_katex()

inline, centred = remove_dollars(find_equations(original_content))

head = """<head>
<meta charset="utf-8">
<link rel="stylesheet" type="text/css" href="lib/katex.min.css">
</head>
"""

body = """<body>
""", content, """
</body>
"""

html = """<!DOCTYPE HTML>
<html>
""", head, """
""", body, """
</html>
"""

with open("katexpage.html", 'w') as f:
    f.write(html)