import os
import io

from PIL import Image

from django.core.urlresolvers import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer

# Custom user model based on Django Auth AbstractUser
from account.models import User

class CrewUploadPhotoTests(APITestCase):

    fixtures = []

    maxDiff = None

    def setUp(self):

        # Normal user
        self.normal_user = User.objects.create(
            first_name="Bob",
            last_name="Green",
            username="bob@green.com",
            email="bob@green.com",
            is_active=True,
            is_staff=False)
        self.normal_user.set_password('demo1234')
        self.normal_user.save()
        self.normal_token, created = Token.objects.get_or_create(
            user=self.normal_user)

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_upload_photo(self):
        """
        Test if we can upload a photo
        """

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.normal_token.key)

        url = reverse('crew-api:upload-photo', args=[self.normal_user.crew.uuid])

        photo_file = self.generate_photo_file()

        data = {
                'photo':photo_file
            }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)