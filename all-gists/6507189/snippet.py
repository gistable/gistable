from django.test import TestCase, RequestFactory
from django.views.generic import TemplateView

from ..lib.views import YourMixin


class YourMixinTest(TestCase):
    '''
    Tests context-data in a Django Mixin like a boss
    '''

    class DummyView(YourMixin, TemplateView):
        '''
        To test get_context_data we need a TemplateView child
        '''
        
        template_name = 'any_template.html'  # TemplateView requires this attribute

    def setUp(self):

        super(YourMixinTest, self).setUp()
        self.request = RequestFactory().get('/fake-path')

        # Setup request and view.
        self.view = self.DummyView()

    def test_context_data_no_args(self):

        # Prepare initial params
        kwargs = {}

        # Launch Mixin's get_context_data
        context = self.view.get_context_data(**kwargs)

        # Your checkings here
        self.assertEqual(context['name'], 'foo')
