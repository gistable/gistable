from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class MyAPICase(APITestCase):

    def setUp(self):
        user = User.objects.create_user('test_user',
                                        'test@email.com', '12345')
        self.client.force_authenticate(user=user)
        self.client.login(username='test_user', password='12345')

        session = self.client.session
        session['some_session_key'] = 'some_session_value'
        session.save()