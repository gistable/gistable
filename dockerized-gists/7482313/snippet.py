"""
py.test demo
~~~~~~~~~~~~

#yolo

"""
from pytest import raises, mark, fixture


# ------------- tidbits ----------------


def test_simple_assert():
    assert False


def test_string_assert():
    assert '1234' == '3456'


def test_complex_assert():
    one = {
        'foo': 'bar',
        'bar': 'foo'
    }

    two = {
        'foo': 'foo',
        'bar': 'bar'
    }
    assert one == two


def test_complex_assert_two():
    one = {
        'foo': 'bar'
    }
    two = {
        'foo': 'bar'
    }
    assert one == two


def test_deep_assert():
    one = {
        'foo': [1, 2, 3]
    }
    two = {
        'foo': [2, 3, 4]
    }
    assert one == two


def test_raises():
    with raises(Exception):
        pass


@mark.skipIf(1 == 2)
def test_skip_on_condition():
    print 'okay, the world is still sane.'


@mark.xfail
def test_mark_as_failed():
    assert False, 'this will fail'


# ------------- fixtures ----------------


class Database(object):

    def __init__(self, name):
        self.name = name


class Client(object):
    def __init__(self, db):
        self.db = db


@fixture(scope='session')
def db():
    return Database('testdb')


@fixture(scope='function')
def client(db):
    return Client(db)


@mark.skipIf(True)
def test_using_database(db):
    assert db.name == 'testdb'
    print id(db)


@mark.skipIf(True)
def test_another_using_database(db):
    assert db.name == 'testdb'
    print id(db)


@mark.skipIf(True)
def test_using_client(client):
    assert client.db.name == 'testdb'
    print id(client)
    print id(client.db)


@mark.skipIf(True)
def test_another_using_client(client):
    assert client.db.name == 'testdb'
    print id(client)
    print id(client.db)


# ------------- monkeypatching ----------------


class XMLConfigurationBeanFactory(object):

    def createConfigurationBean(self):
        return {
            'foo': 'bar'
        }


def test_monkeypatching(monkeypatch):
    monkeypatch.setattr(XMLConfigurationBeanFactory,
                        'createConfigurationBean',
                        lambda self: False)

    factory = XMLConfigurationBeanFactory()
    assert not factory.createConfigurationBean()


def test_monkeypatching_side_effects(monkeypatch):
    factory = XMLConfigurationBeanFactory()
    assert factory.createConfigurationBean() == {'foo': 'bar'}


# ------------- parametrization ----------------


def square(val):
    return val ** 2


@mark.parametrize('input,expected', [
    (2, 4),
    (3, 9),
    (4, 16)
])
def test_square(input, expected):
    assert square(input) == expected


