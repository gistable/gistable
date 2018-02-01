"""Flask Blueprint sublcass that overrides `route`.

Automatically adds rules for endpoints with and without trailing slash.
"""
from flask import Blueprint, Flask


class BaseBlueprint(Blueprint):

    """The Flask Blueprint subclass."""

    def route(self, rule, **options):
        """Override the `route` method; add rules with and without slash."""
        def decorator(f):
            new_rule = rule.rstrip('/')
            new_rule_with_slash = '{}/'.format(new_rule)
            super(BaseBlueprint, self).route(new_rule, **options)(f)
            super(BaseBlueprint, self).route(new_rule_with_slash, **options)(f)
            return f
        return decorator


blueprint = BaseBlueprint('blueprint', __name__)


@blueprint.route('/test/', methods=['POST'])
def test():
    """Simple example; return 'ok'."""
    return 'ok'


@blueprint.route('/test2', methods=['POST'])
def test2():
    """Simple example; return 'ok'."""
    return 'ok'

app = Flask('my_app')
app.register_blueprint(blueprint)

app.run(port=9001)

# Now `/test`, `/test/`, `/test2`, and `/test2/` are registered and can accept
# POSTs without having worry about redirects.
