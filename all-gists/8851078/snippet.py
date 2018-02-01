"""
Unit testing Kivy is easy, but requires a little boiler plate to keep the
window quiet while you test your code.  This is one way to set up py.test, 
but the same technique can probably be used with other test runners as well.

More information on how these py.test hooks work:
http://pytest.org/latest/plugins.html#generic-runtest-hooks
"""
import mock

from kivy.base import EventLoopBase


def pytest_runtest_setup(item):
    item.mock_patches = [
        mock.patch('kivy.uix.widget.Builder'),
        mock.patch.object(EventLoopBase, 'ensure_window', lambda x: None),
    ]
    for patch in item.mock_patches:
        patch.start()


def pytest_runtest_teardown(item, nextitem):
    for patch in item.mock_patches:
        patch.stop()