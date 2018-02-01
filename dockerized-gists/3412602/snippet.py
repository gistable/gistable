import inspect
from flask import Flask


def expose(f):
    """Decorator that flags a method to be exposed"""
    f._exposed_method = True
    return f


class FlaskOfCherryPy(Flask):
    """Custom flask that allows cherrypy's expose decorator"""
    def quickstart(self, root_handler, *args, **kwargs):
        self._process_root_handler(root_handler)
        self.run(*args, **kwargs)

    def _process_root_handler(self, root_handler):
        # Prime the recursive processing
        root_url = []
        self._process_a_handler(root_handler, root_url)

    def _process_a_handler(self, current_handler, url_stack):
        # This gives a list of all the members of current_handler
        members = inspect.getmembers(current_handler)
        for name, value in members:
            # You probably want to skip things that start with a _ or __
            if name.startswith('_'):
                continue
            
            # Check if the method is decorated
            is_exposed_method = getattr(value, '_exposed_method', False)

            # If it's a callable with the _exposed_method attribute set
            # Then it's an exposed method
            if is_exposed_method and callable(value):
                self._add_exposed_url(url_stack, name, value)
            else:
                new_stack = url_stack[:]
                new_stack.append(name)
                self._process_a_handler(value, new_stack)

    def _add_exposed_url(self, url_stack, name, view_func):
        copied_stack = url_stack[:]

        if name != 'index':
            copied_stack.append(name)

        url = "/%s" % "/".join(copied_stack)

        if name == 'index':
            copied_stack.append(name)

        view_name = "_".join(copied_stack)
        self.add_url_rule(url, view_name, view_func)


class Root(object):
    @expose
    def index(self):
        return 'my app'


class Greeting(object):
    def __init__(self, name, greeting):
        self.name = name
        self.greeting = greeting

    @expose
    def index(self):
        return '%s %s!' %(self.greeting, self.name)

    @expose
    def again(self):
        return '%s again, %s!' %(self.greeting, self.name)


if __name__ == '__main__':
    root = Root()
    root.hello = Greeting('Foo', 'Hello')
    root.bye = Greeting('Bar', 'Bye')
    app = FlaskOfCherryPy(__name__)
    app.quickstart(root)