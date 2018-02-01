class LanguageMiddleware(object):
    """
    Detect the user's browser language settings and activate the language.
    If the default language is not supported, try secondary options.  If none of the
    user's languages are supported, then do nothing.
    """

    def is_supported_language(self, language_code):
        supported_languages = dict(settings.LANGUAGES).keys()
        return language_code in supported_languages

    def get_browser_language(self, request):
        browser_language_code = request.META.get('HTTP_ACCEPT_LANGUAGE', None)
        if browser_language_code is not None:
            logging.info('HTTP_ACCEPT_LANGUAGE: %s' % browser_language_code)
            languages = [language for language in browser_language_code.split(',') if
                         '=' not in language]
            for language in languages:
                language_code = language.split('-')[0]
                if self.is_supported_language(language_code):
                    return language_code
                else:
                    logging.info('Unsupported language found: %s' % language_code)

    def process_request(self, request):
        language_code = self.get_browser_language(request)
        if language_code:
            translation.activate(language_code)
            
            
class LanguageMiddlewareTest(BaseMiddlewareTest):

    language_middleware = LanguageMiddleware()

    def test_parse_http_accept_language(self):
        request = self.factory.get('/')
        request.META['HTTP_ACCEPT_LANGUAGE'] = 'de-DE,de;q=0.8,en-GB;q=0.6,en;q=0.4,en-US;q=0.2'
        language_code = self.language_middleware.get_browser_language(request)
        self.assertEqual(language_code, 'de')

    def test_parse_http_accept_language_not_set(self):
        request = self.factory.get('/')
        language_code = self.language_middleware.get_browser_language(request)
        self.assertIsNone(language_code)

    def test_parse_http_accept_language_empty(self):
        request = self.factory.get('/')
        request.META['HTTP_ACCEPT_LANGUAGE'] = ''
        language_code = self.language_middleware.get_browser_language(request)
        self.assertIsNone(language_code)

    def test_parse_http_accept_language_unsupported_language_fallback(self):
        """if language is not supported, try the next one"""
        request = self.factory.get('/')
        request.META['HTTP_ACCEPT_LANGUAGE'] = 'jp,de-DE,de;q=0.8,en-GB;q=0.6,en;q=0.4,en-US;q=0.2'
        language_code = self.language_middleware.get_browser_language(request)
        self.assertEqual(language_code, 'de')

    def test_parse_http_accept_language_unsupported_language_fallback(self):
        """if language is not supported, try the next one"""
        request = self.factory.get('/')
        request.META['HTTP_ACCEPT_LANGUAGE'] = 'jp'
        language_code = self.language_middleware.get_browser_language(request)
        self.assertIsNone(language_code)
