from django.template import Template
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import (
    setup_test_template_loader,
    restore_template_loaders,
    override_settings,
)

class TemplateTest(TestCase):

    def setUp(self):
        templates = {
            "template.html": Template("content here"),
        }
        setup_test_template_loader(templates)

    def tearDown(self):
        restore_template_loaders()

    @override_settings(LOGIN_URL="/login/")
    def test_view(self):
        request = RequestFactory().get("/")