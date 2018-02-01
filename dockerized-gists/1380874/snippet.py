import sys
import unittest
import jinja2


# sys._getframe works on CPython and PyPy. Not tested elsewhere
rs = lambda text: text.format(**sys._getframe(1).f_locals)

def rj(text):
    template = jinja2.Template(text)
    return template.render(sys._getframe(1).f_locals)


class TestRubyStringFormat(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(rs('Foo bar. Or not.'), 'Foo bar. Or not.')

    def test_local_variables_are_used_to_format_text(self):
        name = 'Dumass'
        self.assertEqual(rs('Hello, {name}!'), 'Hello, Dumass!')

    def test_inside_namespace(self):
        def show(user, time):
            return rs("{user.name} is {user.age} {time} old.")
        User = type('User', (object,), {})
        user = User()
        user.name = 'Foobar'
        user.age = 21
        self.assertEqual(show(user, 'years'), 'Foobar is 21 years old.')


class TestJinjaStringRendering(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(rj('Foobar'), 'Foobar')

    def test_local_variables_are_used_to_format_text(self):
        name = 'Dumass'
        self.assertEqual(rj('Hello, {{ name }}!'), 'Hello, Dumass!')

    def test_inside_namespace(self):
        def show(user, time):
            return rj("{{ user.name.capitalize() }} is {{ user.age }} {{ time }} old.")
        User = type('User', (object,), {})
        user = User()
        user.name = 'foobar'
        user.age = 21
        self.assertEqual(show(user, 'years'), 'Foobar is 21 years old.')


if __name__ == '__main__':
    unittest.main()
