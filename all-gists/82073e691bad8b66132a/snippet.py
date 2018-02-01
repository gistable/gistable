import ipdb
import pytest


@pytest.fixture(scope='function')
def resource_a(request):
    default_value = '2'

    if request.scope == 'function' and 'value' in request.funcargnames:
        default_value = request.getfuncargvalue('value')

    print('\nCreating {} objects'.format(default_value))

    def fin():
        print('\nDeleting {} objects'.format(default_value))

    request.addfinalizer(fin)
    return default_value


class TestSomeFixtures(object):
    @pytest.mark.parametrize('value', ['5', '7'])
    def test_variable_fixture_values(self, resource_a, value):
        current_resource = resource_a
        print 'Got Fixture with resource: ' + current_resource
        assert current_resource

    def test_simple_test(self, resource_a):
        current_resource = resource_a
        print 'Got Fixture with resource: ' + current_resource
        assert current_resource
        
py.test -v -s sandbox.py
============================= test session starts ==============================
platform linux2 -- Python 2.7.6 -- py-1.4.20 -- pytest-2.5.2 -- /usr/bin/python
plugins: instafail, xdist
collected 3 items 

sandbox.py:22: TestSomeFixtures.test_variable_fixture_values[5] 
Creating 5 objects
Got Fixture with resource: 5
PASSED
Deleting 5 objects

sandbox.py:22: TestSomeFixtures.test_variable_fixture_values[7] 
Creating 7 objects
Got Fixture with resource: 7
PASSED
Deleting 7 objects

sandbox.py:28: TestSomeFixtures.test_simple_test 
Creating 2 objects
Got Fixture with resource: 2
PASSED
Deleting 2 objects
