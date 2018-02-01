# PEG parser using parsimonious
from parsimonious.grammar import Grammar
from pprint import pprint

# MUST USE " - double quote in regex literal or gave very strange error messagas 
# comment handling seems very difficult...
grammar = Grammar(
    '''
    record = name "=" value
    name = _ ~"\w+" _
    value = _ (recordlist / list / literal) _
    literal = _ (string / number) _
    string = ~"\\".+\\""
    number = ~"[\d\.]+"
    list = "[" elements "]"
    elements = (literal ("," literal)*)?
    recordlist = "{" record+ "}"
    _ = ~"\s*"
    '''
)

def parsi_parse(s):
    # tree is already built, desent recurse to build the dict
    root = grammar.parse(s)

    # each grouping, regex literal match has a node with no expr_name
    # a very funky tree visiting pattern
    # here node is the raw node, but children is processed children
    def default(node, children):
        return children

    def record(node, children):
        return (children[0], children[2])

    def name(node, children):
        return node.children[1].text

    def value(node, children):
        return children[1][0] # grouping

    def string(node, children):
        return node.text[1:-1]

    def number(node, children):
        if '.' in node.text:
            return float(node.text)
        else:
            return int(node.text)

    def literal(node, children):
        return children[1][0]

    def list(node, children):
        return children[1]

    def elements(node, children):
        if not children:
            return []
        else:
            # need to print the nodes to sort this through
            # [first-child] + [",", other-child] 
            return children[0][:1] + [other[1] for other in children[0][1]]

    def recordlist(node, children):
        return dict(children[1])

    def comment(node, children):
        return None

    def _(node, children):
        return None

    parse_locals = locals()
    def visit(node):
        method = parse_locals.get(node.expr_name, default)
        # pre order tree recursion here
        return method(node, [visit(child) for child in node.children])

    return visit(root)


if __name__ == '__main__':
    s = '''
NAME = {
    KEY1 = "Value"
    KEY2 = ["These are my twisted words", 253, 20.0]
    NEST_NAME = {
        KEY3 = "Value"
        KEY4 = ["heh"]
    }
    KEY5 = [253, "Daily Days"]
    KEY8 = ["Fuck", 253, 20.0]
}   
'''
    root = parsi_parse(s)
    pprint(root)
