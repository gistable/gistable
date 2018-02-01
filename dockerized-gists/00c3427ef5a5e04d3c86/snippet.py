#!/usr/bin/env python


class Node(object):
    def __init__(self, params, children):
        self.params = params
        self.children = children


class IfNode(Node):

    def render(self, context):
        test = eval(self.params['test'], globals(), context)
        if test:
            yield iter(self.children)


class ForNode(Node):

    def render(self, context):
        src = eval(self.params['src'], globals(), context)
        dst = self.params['dst']
        for obj in src:
            context[dst] = obj
            yield iter(self.children)


def render(template, **context):
    output = []
    stack = [iter(template)]

    while stack:
        node = stack.pop()
        if isinstance(node, basestring):
            output.append(node.format(**context))
        elif isinstance(node, Node):
            stack.append(node.render(context))
        else:
            new_node = next(node, None)
            if new_node is not None:
                stack.append(node)
                stack.append(new_node)
    return "".join(output)


if __name__ == "__main__":
    template = [
        "<h1>Hobbit Index</h1>",
        "<ul>",
        ForNode(
            {"src": "hobbits", "dst": "hobbit"},
            [
                "<li",
                IfNode(
                    {"test": "hobbit==active"},
                    [
                        ' class="active"'
                    ]
                ),
                ">",
                "{hobbit}",
                "</li>",
            ]
        ),
        "</ul>"
    ]
    print render(template,
                 hobbits=['Sam', 'Frodo', "Bilbo"],
                 active="Frodo")
