"""
Replaces unittest style asserts (e.g.: self.assertEqual) with py.test style asserts

Usage:

    from lib2to3.refactor import RefactoringTool

    refactoring_tool = RefactoringTool(['fix_pytest'])
    refactoring_tool.refactor(['input.py'], write=True)
"""

from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import syms, String


TWO_ARGS = {
    'assertEqual': '==',
    'assertEquals': '==',
    'assertDictEqual': '==',
    'assertNotEquals': '!=',
    'assertNotEqual': '!=',
    'assertGreater': '>',
    'assertIn': 'in',
    'assertNotIn': 'not in',
    'assertIs': 'is',
}

ONE_ARG = ['assertTrue', 'assertFalse', 'assert200', 'assert400', 'assertIsNotNone', 'assertIsNone']

class FixPytest(BaseFix):

    PATTERN = """
    power< self='self'
           trailer< dot='.' method=({}) >
           trailer< lparen='(' args=(arglist | [any]) rparen=')' > >
    """.format('|'.join([repr(k) for k in TWO_ARGS.keys() + ONE_ARG]))

    def transform(self, node, results):
        method = results['method'][0].value

        explain = None

        if method in TWO_ARGS:
            assert len(results['args'][0].children) in (3, 5)

            left, _, right = results['args'][0].children[:3]

            left.prefix = ' '
            left.changed()
            right.prefix = ' '
            right.changed()
            comparasion = String(TWO_ARGS[method])
            comparasion.prefix = ' '

            if len(results['args'][0].children) > 3:
                explain = results['args'][0].children[4]

            output = [left, comparasion, right]

        elif method in ONE_ARG:
            if results['args'][0].type != syms.arglist:  # Only one argument passed
                args = [results['args'][0]]
            else:
                args = results['args'][0].children

            args[0].prefix = ' '
            args[0].changed()

            if method == 'assertTrue':
                output = [args[0]]
            elif method == 'assertFalse':
                output = [String(' not'), args[0]]
            elif method == 'assert200':
                output = [args[0], String('.status_code == 200')]
            elif method == 'assert400':
                output = [args[0], String('.status_code == 400')]
            elif method == 'assertIsNotNone':
                output = [args[0], String(' is not None')]
            elif method == 'assertIsNone':
                output = [args[0], String(' is None')]

            if len(args) > 1:
                explain = args[2]

        if explain:
            explain.prefix = ' '
            explain.changed()
            output += [String(','), explain]

        return [String(results['node'].prefix + 'assert')] + output
