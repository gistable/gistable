"""pytest configuration and utilities."""

import os
from urllib.parse import urlparse

from flask.ext.migrate import upgrade
import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from pygotham.core import db
from pygotham.factory import create_app
from tests import settings


@pytest.fixture(scope='session')
def app():
    app = create_app(__name__, '', settings)

    context = app.test_request_context()
    context.push()

    return app


@pytest.fixture(scope='session', autouse=True)
def setup_db(request, app):
    db_name = urlparse(app.config['SQLALCHEMY_DATABASE_URI']).path[1:]
    if os.system("psql -l | grep '{}'".format(db_name)) == 0:
        assert not os.system('dropdb {}'.format(db_name))
    assert not os.system('createdb -E utf-8 {}'.format(db_name))

    upgrade()

    @event.listens_for(Session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()


@pytest.fixture(autouse=True)
def dbsession(request):
    request.addfinalizer(db.session.remove)

    db.session.begin_nested()