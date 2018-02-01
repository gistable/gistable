import pytest


@pytest.fixture()
def real_db(_django_cursor_wrapper):
    _django_cursor_wrapper.enable()


def test_index(client, real_db):
    response = client.get('/')
    assert response.status_code == 200
