# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import, division

import pytest
from django_webtest import DjangoTestApp, WebTestMixin


class Stub(object):
    """Stub methods, keep track of calls."""

    def __init__(self, monkeypatch):
        self.monkeypatch = monkeypatch
        self.stubbed = {}

    def stub(self, obj, **kwargs):
        """Stub obj.method to return whatever parameter was passed for method.

        Usage: stub(django.utils.timezone, now='now')

        It's possible to stub several methods on the same object at once.

        """
        self.stubbed.setdefault(obj, {})
        for method, val in kwargs.items():
            self._stub(obj, method, val)
        return self.stubbed[obj]

    def _stub(self, obj, method, value):
        """Wrap the value to be returned, to check for its calls."""

        def call(*args, **kwargs):
            """Return the value monkeypatched for this method, track call."""
            self.stubbed[obj][method].append({'args': args, 'kwargs': kwargs})
            return value(*args, **kwargs)

        self.stubbed[obj][method] = []  # new stub: reset calls, if any
        self.monkeypatch.setattr(obj, method, call)


@pytest.fixture(scope='function')
def stubber(monkeypatch):
    """Provides stubbing capabilities."""
    return Stub(monkeypatch)


@pytest.fixture(scope='function')
def stub_save(stubber):
    """Stub the Model.save() method to avoid database access."""
    from django.db.models import Model

    def stubbed_save(self, *args, **kwargs):
        return 'no database access'

    stubbed = stubber.stub(Model, save=stubbed_save)
    return stubbed['save']


@pytest.fixture(scope='session')
def setup_view():
    def _setup_view(view, request, *args, **kwargs):
        """Mimic as_view() returned callable, but returns a view instance.

        args and kwargs are the same you would pass to ``reverse()``

        """
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

    return _setup_view


@pytest.fixture(scope='function')
def app():
    """WebTest's TestApp.

    Patch and unpatch settings before and after each test.

    WebTestMixin, when used in a unittest.TestCase, automatically calls
    _patch_settings() and _unpatchsettings.

    """
    wtm = WebTestMixin()
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return DjangoTestApp()