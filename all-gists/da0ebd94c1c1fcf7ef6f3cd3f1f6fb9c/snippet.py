import tempfile
from PIL import Image


class PhotoCreateAPIViewTest(TestCase):
    
    def setUp(self):
        super().setUp()
        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image = Image.new('RGB', (100, 100))
        image.save(self.tmp_file.name)
        self.params = {
            'photo': self.tmp_file
        }

    def test_valid_authenticated_post_returns_201(self):
        response = self.auth_client.post(
            reverse(self.view_name), data=self.params, format='multipart')
    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)