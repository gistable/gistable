#!/usr/bin/env python
"""
mocking requests calls

"""
import mock
import unittest
import requests
from requests.exceptions import HTTPError


def google_query(query):
    """
    trivial function that does a GET request
    against google, checks the status of the
    result and returns the raw content

    """
    url = "https://www.google.com"
    params = {'q': query}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.content


class TestRequestsCall(unittest.TestCase):
    """
    example text that mocks requests.get and
    returns a mock Response object
    """
    def _mock_response(
            self,
            status=200,
            content="CONTENT",
            json_data=None,
            raise_for_status=None):
        """
        since we typically test a bunch of different
        requests calls for a service, we are going to do
        a lot of mock responses, so its usually a good idea
        to have a helper function that builds these things

        """
        mock_resp = mock.Mock()
        # mock raise_for_status call w/optional error
        mock_resp.raise_for_status = mock.Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        # set status code and content
        mock_resp.status_code = status
        mock_resp.content = content
        # add json data if provided
        if json_data:
            mock_resp.json = mock.Mock(
                return_value=json_data
            )
        return mock_resp

    @mock.patch('requests.get')
    def test_google_query(self, mock_get):
        """test google query method"""
        mock_resp = self._mock_response(content="ELEPHANTS")
        mock_get.return_value = mock_resp

        result = google_query('elephants')
        self.assertEqual(result, 'ELEPHANTS')
        self.failUnless(mock_resp.raise_for_status.called)

    @mock.patch('requests.get')
    def test_failed_query(self, mock_get):
        """test case where google is down"""
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("google is down"))
        mock_get.return_value = mock_resp
        self.assertRaises(HTTPError, google_query, 'elephants')

if __name__ == '__main__':
    unittest.main()
