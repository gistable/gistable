import falcon
import falcon.testing as testing

QUOTE = (u"\nI've always been more interested in\n"
         u'the future than in the past.\n'
         u'\n'
         u'    ~ Grace Hopper\n\n')

class ThingsResource(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.body = QUOTE

class TestThings(testing.TestBase):
    def before(self):
        things = ThingsResource()
        # TestBase provides an instance of falcon.API to use along
        # with simulate_request (see below).
        self.api.add_route('/things', things)

    def test_grace(self):
        # TestBase provides a method to simulate a WSGI request without
        # having to stand up an actual server. The decode option tells
        # simulate_request to convert the raw WSGI response into a
        # Unicode string.
        body = self.simulate_request('/things', decode='utf-8')

        # TestBase provides an instance of StartResponseMock that captures
        # the data passed to WSGI's start_response callback. This includes
        # the status code and headers returned by the Falcon app.
        self.assertEqual(self.srmock.status, falcon.HTTP_200)
        self.assertEqual(body, QUOTE)
