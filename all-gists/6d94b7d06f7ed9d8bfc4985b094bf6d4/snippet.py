from django.utils.encoding import force_text
from django.template.base import TemplateSyntaxError
from django.template.library import Library, Node

register = Library()


@register.simple_tag
def assign(value):
    '''
    Examples:
       {% assign 'A value' as a_variable %}
       {% assign another_variable as a_variable %}

    '''
    return value


@register.tag
def modify(parser, token):
    '''
    Examples:
        {% modify a_variable += a_value %}
        {% modify a_variable += ' hello' %}
        {% modify a_variable *= 2 %}

    Available operators: += -= *= /= %= //= **= <<= >>= &= |=
    '''
    parts = token.split_contents()
    if len(parts) < 2:
        raise TemplateSyntaxError("'modify' statements should have four words: %s" % token.contents)

    var_name, op, value = parts[1:4]
    value = parser.compile_filter(value)

    class OpNode(Node):
        child_nodelists = tuple()

        def add(self, context): context[var_name] += value.resolve(context)
        def sub(self, context): context[var_name] -= value.resolve(context)
        def mul(self, context): context[var_name] *= value.resolve(context)
        def div(self, context): context[var_name] /= value.resolve(context)
        def mod(self, context): context[var_name] %= value.resolve(context)
        def floordiv(self, context): context[var_name] //= value.resolve(context)
        def pow(self, context): context[var_name] **= value.resolve(context)
        def lhs(self, context): context[var_name] <<= value.resolve(context)
        def rhs(self, context): context[var_name] >>= value.resolve(context)
        def bin_and(self, context): context[var_name] &= value.resolve(context)
        def bin_or(self, context): context[var_name] |= value.resolve(context)

        def render(self, context):
            {
                '+=': self.add,
                '-=': self.sub,
                '*=': self.mul,
                '/=': self.div,
                '%=': self.mod,
                '//=': self.floordiv,
                '**=': self.pow,
                '<<=': self.lhs,
                '>>=': self.rhs,
                '&=': self.bin_and,
                '|=': self.bin_or,
            }[op](context)

            return ''

    return OpNode()


@register.tag
def operate(parser, token):
    '''
    Examples:
        {% operate a + b - 1 %}
        {% operate a * 2 as result %}
        {% operate ( a + b ) /2 as the_average %}
        {% operate s|stringformat:'%04d' + ' my-suffix' as string_operations %}

    -> Expressions with python operators
    -> Only one constraint: embed with spaces the variables and the sub-expressions with filters,
                            do not glue variables, operators, and string litterals
       but operators and numbers litterals can be glued as that: ( v +4)
    '''
    parts = token.split_contents()
    target_var = None
    if parts[-2] == 'as':
        target_var = parts[-1]
        parts = parts[:-2]

    expression_parts = []
    vars = dict()

    for part in parts[1:]:
        if (part[0] in '+-*/%~<>=()&|!0123456789"\'') or (part in ('and', 'or')):
            expression_parts.append(part)
            continue

        var_name = 'v%d' % len(vars)
        expression_parts.append(var_name)

        vars[var_name] = parser.compile_filter(part)

    expression = ' '.join(expression_parts)

    class ExprNode(Node):
        child_nodelists = tuple()

        def render(self, context):
            res = eval(expression, { k: var.resolve(context) for k, var in vars.items() })

            if target_var is None:
                return force_text(res)

            context[target_var] = res

            return ''

    return ExprNode()
