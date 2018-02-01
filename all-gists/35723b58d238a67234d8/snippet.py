#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
A lint tool for robotframework cases, only one py file script.

There is one lint tool for robotframework on github https://github.com/boakley/robotframework-lint,
but it only support static analysis on plain text.
We have many case in html format, and once more, the parsed robotframework suite also need to check.
So I write this script here.

Robotframework best practices:
    http://becrtt01.china.nsn-net.net/cleancode/codingcookbook/blob/master/robotframework_best_practices.md

Supported checking points:

## W101
* show bad suite/case/keyword/variable name warning
    * suite name should not contain "."
    * suite name should not be less than 3 words
    * test name should not contain "."
    * test name should not be the same as suite name
    * suite variable should be upper case
    * scalar variable should not contain more than one value
    * list variable should not contain only one value
## W102
* show too little/many test cases in one suite warning
* show too little/too many steps in one test case warning
* show too many steps in one keyword warning
* show too many arguments in one keyword warning
* show no __init__.html warning (neither suite setup nor suite teardown defined)
## E103
* show mandentory tags missing warning
## W201
* show some dangerous keywords like (Fatal Error) usage warning (or error)
* show set global variable usage warning
* show set suite variable/set test variable invalid usage warning
* show deprecated keywords used warning
* use "Run Keyword and Ignore Error" but no return value used warning
* performance issue warning like using sleep
* recursive calling
## W202
* show case duplication warning
## TODO
* show hard coded warning
* unused resource file/library file warning
* show dry-run warning or errors
'''
import sys
import os
import hashlib
from robot.model import SuiteVisitor
from robot import get_version
if get_version() < '2.8.0':
    raise RuntimeError('RobotFramework 2.8+ required!')
from robot.api import TestSuiteBuilder, TestSuite
from robot.running.model import TestCase

default_settings = {
    'MAX_CASES_IN_ONE_SUITE': 10,
    'MIN_CASES_IN_ONE_SUITE': 2,
    'MAX_STEPS_IN_ONE_CASE': 10,
    'MIN_STEPS_IN_ONE_CASE': 2,
    'MAX_STEPS_IN_ONE_KW': 15,
    'FORBIDDEN_KEYWORDS': ('Fatal Error', 'Set Global Variable'),
    'MANDATORY_TAGS': ('owner', ),
    'MAX_ARGUMENTS_IN_ONE_KEYWORD': 5,
    'DEPRECATED_KEYWORDS': ('Create File With Encoding', ),
    }

def load_settings(_settings):
    class _Settings(object):
        def __init__(self, _settings):
            self._settings = _settings

        def __getattr__(self, attr):
            return self._settings[attr]

    return _Settings(_settings)

try:
    import settings
except ImportError:
    settings = load_settings(default_settings)


class LintBuilder(object):
    def __init__(self, _suite, _findings):
        self._suite = _suite
        self._findings = _findings
        self._checkers = None

    def build(self):
        ''' scan all available checkers, and sort them with _id '''
        _checkers = []
        for cls in globals():
            if cls.endswith('Checker') and not cls.startswith('_'):
                inst = globals()[cls](self._findings)
                _checkers.append(inst)
        self._checkers = CombinedCheckers(sorted(_checkers, key=lambda x: x._id))
        return self

    def lint(self):
        ''' do the static analysis '''
        self._suite.visit(self._checkers)
        self._findings.visit()
        sys.exit(self._findings.get_code())


class CombinedCheckers(SuiteVisitor):
    def __init__(self, checkers):
        super(CombinedCheckers, self).__init__()
        self._checkers = checkers

    def start_suite(self, suite):
        for _checker in self._checkers:
            _checker.start_suite(suite)

    def end_suite(self, suite):
        for _checker in self._checkers:
            _checker.end_suite(suite)

    def start_test(self, test):
        for _checker in self._checkers:
            _checker.start_test(test)

    def end_test(self, test):
        for _checker in self._checkers:
            _checker.end_test(test)

    def start_keyword(self, kw):
        for _checker in self._checkers:
            _checker.start_keyword(kw)

    def end_keyword(self, kw):
        for _checker in self._checkers:
            _checker.end_keyword(kw)


class Findings(object):
    ''' Findings of all checking actions '''
    def __init__(self):
        self._findings = []

    def add(self, _finding):
        self._findings.append(_finding)

    def visit(self):
        if self._findings:
            print 'Severity\tCategory\tNode\tMessage'
            for _finding in self._findings:
                print self.format_finding(_finding)
        else:
            print 'Great, You are awsome!'

    def format_finding(self, _finding):
        return '%s%s\t%s\t%s\t%s' % _finding

    def get_code(self):
        return len(self._findings)


class _BaseChecker(SuiteVisitor):
    ''' This is a VIRTUAL checker, that will be inherited by others '''
    _id = 0
    _severity = 'R' # E/W/R
    _name = 'base'

    def __init__(self, _findings):
        SuiteVisitor.__init__(self)
        self._findings = _findings

    def add_finding(self, category, node, msg):
        self._findings.add((self._severity, self._id, category, node, msg))


class NamingChecker(_BaseChecker):
    '''
    * show bad suite/case/keyword/variable name warning
        * suite name should not contain "."
        * suite name should not be less than 3 words
        * test name should not contain "."
        * test name should not be the same as suite name
        * suite variable should be upper case
        * scalar variable should not contain more than one value
        * list variable should not contain only one value
    '''
    _id = 101
    _severity = 'W'
    _name = 'bad-name'

    def start_suite(self, _suite):
        if os.path.isdir(_suite.source):
            if '.' in os.path.basename(_suite.source):
                self.add_finding('suite', os.path.basename(_suite.source),
                        'suite name should not contain "."')
        else:
            if os.path.basename(_suite.source).count('.') > 1:
                self.add_finding('suite', os.path.basename(_suite.source),
                        'suite name should not contain "."')
        if not _suite.suites and len(_suite.name.split()) < 3:
            self.add_finding('suite', _suite.name,
                    'suite name should not be less than 3 words')
        for _variable in _suite.variables:
            self._check_suite_variable_name(_variable)


    def start_test(self, _test):
        if '.' in _test.name:
            self.add_finding('test', _test.name,
                    'test name should contain "."')
        if _test.name == _test.parent.name:
            self.add_finding('test', _test.name,
                    'test name should not be the same with suite name')

    def _check_suite_variable_name(self, _variable):
        if _variable.name.upper() != _variable.name:
            self.add_finding('variable', _variable.name,
                    'suite variable name should be upper case')
        if _variable.name.startswith('$') and len(_variable.value) > 1:
            self.add_finding('variable', _variable.name,
                    'scalar variable should not contain more than one value')
        if _variable.name.startswith('@') and len(_variable.value) == 1:
            self.add_finding('variable', _variable.name,
                    'list variable should not contain only one value')


class StructureChecker(_BaseChecker):
    '''
    * show too little/many test cases in one suite warning
    * show too little/too many steps in one test case warning
    * show too many steps in one keyword warning
    '''
    _id = 102
    _severity = 'W'
    _name = 'bad-structure'

    def start_suite(self, _suite):
        self._check_cases_in_suite(_suite)
        self._check_setup_teardown_in_suite(_suite)

    def _check_cases_in_suite(self, _suite):
        if _suite.tests:
            if len(_suite.tests) < settings.MIN_CASES_IN_ONE_SUITE:
                self.add_finding('suite', _suite.name,
                        'one suite contain less than %d tests' % settings.MIN_CASES_IN_ONE_SUITE)
            elif len(_suite.tests) > settings.MAX_CASES_IN_ONE_SUITE:
                self.add_finding('suite', _suite.name,
                        'one suite contain more than %d tests' % settings.MAX_CASES_IN_ONE_SUITE)
    def _check_setup_teardown_in_suite(self, _suite):
        if not _suite.keywords.setup and not _suite.keywords.teardown:
            self.add_finding('suite', _suite.name,
                    'neither setup nor teardown defined')

    def start_test(self, _test):
        if _test.template:
            num_of_steps = len(self._get_steps(self._get_steps(_test)[0]))
            if num_of_steps == 0: # when template contain variable
                return
        else:
            num_of_steps = len(self._get_steps(_test))
        if num_of_steps < settings.MIN_STEPS_IN_ONE_CASE:
            self.add_finding('test', _test.name,
                    'one test contain less than %d steps' % settings.MIN_STEPS_IN_ONE_CASE)
        elif num_of_steps > settings.MAX_STEPS_IN_ONE_CASE:
            self.add_finding('test', _test.name,
                    'one test contain more than %d steps' % settings.MAX_STEPS_IN_ONE_CASE)

    def start_keyword(self, _kw):
        self._check_steps_in_one_kw(_kw)
        self._check_arguments_in_one_kw(_kw)

    def _check_steps_in_one_kw(self, _kw):
        if len(self._get_steps(_kw)) > settings.MAX_STEPS_IN_ONE_KW:
            self.add_finding('keyword', _kw.name,
                    'one keyword contain more than %d steps' % settings.MAX_STEPS_IN_ONE_KW)

    def _check_arguments_in_one_kw(self, _kw):
        if len(_kw.args) > settings.MAX_ARGUMENTS_IN_ONE_KEYWORD:
            self.add_finding('keyword', _kw.name,
                    'too many arguments (%d/%d)' % (len(_kw.args),
                        settings.MAX_ARGUMENTS_IN_ONE_KEYWORD))

    def _get_steps(self, parent):
        return filter(lambda _kw: _kw.is_comment() is False, parent.keywords)


class TagsChecker(_BaseChecker):
    '''
    * show mandentory tags missing warning
    '''
    _id = 103
    _severity = 'E'
    _name = 'mandentory-tags'

    def start_test(self, _test):
        tags = self._get_tags(_test)
        missing_tags = filter(lambda _tag: tags.get(_tag, '') == '', settings.MANDATORY_TAGS)
        if missing_tags:
            self.add_finding('test', _test.name,
                    'mandatory tags %s missing or empty value' % str(missing_tags))

    def _get_tags(self, _test):
        return dict(map(lambda _tag: '-' in _tag and _tag.split('-', 1) or [_tag, ''], _test.tags))


class KeywordInvalidUsageChecker(_BaseChecker):
    '''
    * show too many arguments in one keyword warning
    * show set suite variable/set test variable invalid usage warning
    * show dangerous keywords usage warning
    * show deprecated keywords used warning
    * use "Run Keyword and Ignore Error" but no return value used warning
    * performance issue warning like using sleep
    * recursive calling
    '''
    _id = 201
    _severity = 'W'
    _name = 'keyword-invalid-usage'

    def start_keyword(self, _kw):
        self._check_arguments(_kw)
        self._check_forbidden(_kw)
        self._check_deprecated(_kw)
        self._check_set_suite_variable(_kw)
        self._check_set_test_variable(_kw)
        self._check_sleep(_kw)
        self._check_run_keyword_and_ignore_error(_kw)
        self._check_recursive_calling(_kw)

    def _check_arguments(self, _kw):
        if len(_kw.args) > settings.MAX_ARGUMENTS_IN_ONE_KEYWORD:
            self.add_finding('keyword', _kw.name,
                    'too many arguments (%d/%d)' % (len(_kw.args),
                        settings.MAX_ARGUMENTS_IN_ONE_KEYWORD))

    def _check_forbidden(self, _kw):
        if _kw.name in settings.FORBIDDEN_KEYWORDS:
            self.add_finding('keyword', _kw.name,
                    'keyword "%s" is forbidden' % _kw.name)

    def _check_deprecated(self, _kw):
        if _kw.name in settings.DEPRECATED_KEYWORDS:
            self.add_finding('keyword', _kw.name,
                    'keyword "%s" is deprecated' % _kw.name)

    def _check_set_suite_variable(self, _kw):
        if _kw.name == 'Set Suite Variable':
            parent = _kw.parent
            while type(parent) not in (TestCase, TestSuite):
                parent = parent.parent
            if type(parent) == TestCase:
                self.add_finding('keyword', _kw.name,
                        'keyword "Set Suite Variable" should not be used in TestCase')

    def _check_set_test_variable(self, _kw):
        if _kw.name == 'Set Test Variable':
            parent = _kw.parent
            while type(parent) not in (TestCase, TestSuite):
                parent = parent.parent
            if type(parent) == TestCase:
                self.add_finding('keyword', _kw.name,
                        'keyword "Set Test Variable" should not be used in TestSuite')

    def _check_sleep(self, _kw):
        if _kw.name == 'Sleep':
            self.add_finding('keyword', _kw.name,
                    'using Sleep may cause performance issue')

    def _check_run_keyword_and_ignore_error(self, _kw):
        if _kw.name == 'Run Keyword and Ignore Error' and not _kw.assign:
            self.add_finding('keyword', _kw.name,
                    'using "Run Keyword and Ignore Error" but with no return value used, \
                    "Run Keyword And Continue On Failure" is your choice')

    def _check_recursive_calling(self, _kw):
        parent = _kw.parent
        while hasattr(parent, 'type') and parent.type == 'kw':
            if parent.name == _kw.name:
                self.add_finding('keyword', _kw.name,
                        'recursive calling detected')
                break
            parent = parent.parent


class CaseDupChecker(_BaseChecker):
    _id = 202
    _severity = 'W'
    _name = 'case-duplication'

    def __init__(self, _findings):
        _BaseChecker.__init__(self, _findings)
        self._cases = {} # key: md5, value: [case longname]

    def start_test(self, _test):
        steps = map(lambda kw: kw.name, _test.keywords)
        _md5 = hashlib.md5(str(steps)).hexdigest()
        self._cases.setdefault(_md5, []).append(_test.longname)
        if len(self._cases[_md5]) > 1:
            self.add_finding('test', _test.name,
                    'duplicated tests %s' % str(self._cases[_md5]))


if __name__ == '__main__':
    paths = sys.argv[1:]
    if '-h' in paths or '--help' in paths:
        print __doc__
        print 'usage:\n\npython rfexplain.py <path 1> <path 2> ...\n'
        sys.exit(0)
    suite = TestSuiteBuilder().build(*paths)
    findings = Findings()
    LintBuilder(suite, findings).build().lint()
