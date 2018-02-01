from django.core.urlresolvers import reverse as r

# ...

class SubscribeViewTest(TestCase):
    def setUp(self):
        self.resp = self.client.get(r('subscriptions:subscribe'))

    def test_get(self):
        'Ao visitar /inscricao/ a página de inscrição é exibida'
        self.assertEquals(200, self.resp.status_code)

    def test_use_template(self):
        self.assertTemplateUsed(self.resp,
                                'subscriptions/subscription_form.html')

    def test_has_form(self):
        'A resposta deve contar o formulário de inscrição'
        self.assertIsInstance(self.resp.context['form'], SubscriptionForm)