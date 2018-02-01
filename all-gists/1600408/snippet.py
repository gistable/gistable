from zope.testbrowser.browser import Browser

def _zope_testbrowser_pyquery(self):
    from pyquery import PyQuery
    return PyQuery(self.contents)

Browser.pyquery = property(_zope_testbrowser_pyquery)

# This will allow you to do in your tests:
# >>> "Home" in browser.pyquery('#navigation').text()

# pyquery docs: http://packages.python.org/pyquery/
# zope.testbrowser docs: http://pypi.python.org/pypi/zope.testbrowser