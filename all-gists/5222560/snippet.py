# -*- coding: utf-8 -*-
import ast

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


json_syntax = r'''
    json_file = ws? json ws?
    json = object / array

    object = "{" members "}"
    members = member_and_comma* member
    member_and_comma = member comma
    member = ws? string ws? ":" value

    array = "[" values "]"
    values = value_and_comma* value
    value_and_comma = value comma

    value = ws? (true / false / object / array / number / string / null) ws?
    true = "true"
    false = "false"
    null = "null"
    number = ~r"-?(0|([1-9][0-9]*))(\.[0-9]+)?([Ee][+-][0-9]+)?"
    string = ~"\"[^\"\\\\]*(?:\\\\.[^\"\\\\]*)*\""is
    ws = ~r"\s+"
    comma = ws? "," ws?
'''
grammar = Grammar(json_syntax)


class JsonVisitor(NodeVisitor):
    """ Produces Python objects from parsed JSON grammar tree
    """
    def generic_visit(self, node, visited_children):
        return visited_children or node

    # helper functions for generic patterns
    def combine_many_or_one(self, node, (members, member)):
        """ Usable for following pattern:

            values = value_and_comma* value
        """
        if isinstance(members, list):
            return members + [member]
        return [member]

    def lift_first_child(self, node, visited_children):
        """ Returns first child from `visited_children`, e.g. for::

            rule = item optional another_optional?

        returns `item`
        """
        return visited_children[0]

    # visitors
    visit_json = lift_first_child

    def visit_json_file(self, node, (eol1, json_, eol)):
        return json_

    def visit_object(self, node, (cb1, members, cb2)):
        return dict(members)

    def visit_array(self, node, (cb1, values, cb2)):
        return values

    visit_member_and_comma = visit_value_and_comma = lift_first_child
    visit_values = visit_members = combine_many_or_one

    def visit_member(self, node, (_1, name, _2, colon, value)):
        return name, value

    def visit_value(self, node, (_1, value, _2)):
        return value[0]

    def visit_string(self, node, visited_children):
        # produce unicode for strings
        return ast.literal_eval("u" + node.text)

    def visit_number(self, node, visited_children):
        return ast.literal_eval(node.text)

    def visit_true(self, node, visited_children):
        return True

    def visit_false(self, node, visited_children):
        return False

    def visit_null(self, node, visited_children):
        return None


def loads(s):
    """ Simulates json.loads() without additional parameters
    """
    tree = grammar.parse(s)
    return JsonVisitor().visit(tree)

# And here some tests and benchmarks
tests = [
    '''[
       "asdf", 1, 2, 3, 2.7, true, false, null] ''',
    '{"single": "member"}',
    '''{"asdf": 123, "zxcv": 456, "qwe": [1, 2, 3.42]}''',
    '''{"asdf": 123, "zxv": true, "qwe": false}''',
    r'''{
     "asdf": "test",
     "zxv": -1,
     "hello world": "\u041f\u0440\u0438\u0432\u0435\u0442 \u043c\u0438\u0440!",
     "inner": {
        "ghg": 321,
        "test": [1, 2, 3]
        }
    }''',
    '''[
        [0, -1, 0],
        [1, 0, 0],
        [0, 0, 1]
    ]''',
    r'''
    {
    "name": "Jack (\"Bee\") Nimble\n\t\b",
    "format": {
        "type":       "rect", 
        "width":      1920, 
        "height":     1080, 
        "interlace":  false, 
        "frame rate": 24
        }
    }'''
]


import json
import timeit


def main():
    NUMBER = 1000
    for test in tests:
        result = loads(test)
        print(result)
        assert result == json.loads(test)
        t_ours = timeit.timeit(lambda: loads(test), number=NUMBER)
        t_json = timeit.timeit(lambda: json.loads(test), number=NUMBER)
        print("It is {0:.3f} ({1:.3f}/{2:.3f}) times slower\n".format(
            t_ours / t_json, t_ours, t_json))


if __name__ == '__main__':
    main()
