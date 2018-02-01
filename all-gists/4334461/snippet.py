"""
filename: angularjs.py

Usage:
    {% ng Some.angular.scope.content %}

e.g.
    {% load angularjs %}
    <div ng-init="yourName = 'foobar'">
        <p>{% ng yourName %}</p>
    </div>
"""

from django import template

register = template.Library()


class AngularJS(template.Node):
    def __init__(self, bits):
        self.ng = bits

    def render(self, ctx):
        return "{{%s}}" % " ".join(self.ng[1:])


def do_angular(parser, token):
    bits = token.split_contents()
    return AngularJS(bits)

register.tag('ng', do_angular)
