import logging

from django.utils import translation


class SubdomainLanguageMiddleware(object):
    """
    Set the language for the site based on the subdomain the request
    is being served on. For example, serving on 'fr.domain.com' would
    make the language French (fr).
    """
    LANGUAGES = ['fr']

    def process_request(self, request):
        host = request.get_host().split('.')
        if host and host[0] in self.LANGUAGES:
            lang = host[0]
            logging.debug("Choosing language: {0}".format(lang))
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
