import pytest


@pytest.fixture()
def user(request):
  user = 'mock user'
  if hasattr(request, 'param'):
    user += ': {}'.format(request.param)
  return user


@pytest.mark.parametrize('user', ('foo',), indirect=True)
def test_foo(user):
  assert user == 'mock user: foo'


@pytest.mark.parametrize('user', ('bar',), indirect=True)
def test_bar(user):
  assert user == 'mock user: bar'


def test_default(user):
  assert user == 'mock user'