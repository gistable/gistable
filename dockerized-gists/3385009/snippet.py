from mock import patch #http://pypi.python.org/pypi/mock
import flask

import myapp

@patch('flask.templating._render', return_value='')
def test_mocked_render(mocked):
    t = myapp.app.test_client()
    print "mocked", repr(t.get("/").data)
    print "was _render called?", mocked.called

def test_normal_render():
    t = myapp.app.test_client()
    print "normal", repr(t.get('/').data)

if __name__ == "__main__":
    test_normal_render()
    test_mocked_render()
    test_normal_render()

#output:
'''
$ ../bin/python tests.py
normal '<html><head></head><body><p>stuff</p></body></html>'
mocked ''
was _render called? True
normal '<html><head></head><body><p>stuff</p></body></html>'
'''
