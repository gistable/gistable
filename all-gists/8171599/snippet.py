# django==1.6.1
# django_facebook==5.3.1

from django.test import TestCase
from django_facebook.models import FacebookCustomUser

class MyTest(TestCase):

    def setUp(self):
        user = FacebookCustomUser()
        user.facebook_id = '123456789'
        user.save()

    def do_login(self):
        self.client.login(facebook_id = '123456789')

    def test_get_api(self):
        self.do_login()
        response = self.client.get(url)
        # do your asserts and other tests here
