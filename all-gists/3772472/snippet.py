import unittest
from app import app
from cStringIO import StringIO

class UploadTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_upload(self):
        res = self.client.post('/', data=dict(
            upload_var=(StringIO("hi everyone"), 'test.txt'),
        ))
        assert res.status_code == 200
        assert 'file saved' in res.data

if __name__ == '__main__':
    unittest.main()
