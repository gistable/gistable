import base64
from myapplication import app

class MyTestCase(unittest.TestCase):
    def setUp(self):    
        self.app = app.test_client()
    
    def tearDown(self):
        pass

    def open_with_auth(self, url, method, username, password):
        return self.app.open(url,
            method=method,
            headers={
                'Authorization': 'Basic ' + base64.b64encode(username + \
                ":" + password)
            }
        )
        
    def test_login(self):
        res = self.open_with_auth('/user/login', 'GET', 'username',
                                  'password')