from django.test import TestCase
import re


class MyTestCase(TestCase):

    @staticmethod
    def remove_csfr(html_code):
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        return re.sub(csrf_regex, '', html_code)

    def assertEqualExceptCSFR(self, html_code1, html_code2):
        return self.assertEqual(
            self.remove_csfr(html_code1),
            self.remove_csfr(html_code2)
        )