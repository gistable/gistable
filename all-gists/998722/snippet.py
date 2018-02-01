import platform
import re
import urllib2
import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.urlresolvers import resolve
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode

try:
    from django.conf import settings
    URL_VALIDATOR_USER_AGENT = settings.URL_VALIDATOR_USER_AGENT
except ImportError:
    # It's OK if Django settings aren't configured.
    URL_VALIDATOR_USER_AGENT = 'Django (http://www.djangoproject.com/)'


class RelativeURLValidator(RegexValidator):
    """ Validator which allows for relative URL's as well. """

    regex = re.compile(
        r'^((?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE) # host is optional, allow for relative URLs

    def __init__(self, verify_exists=False, validator_user_agent=URL_VALIDATOR_USER_AGENT):
        super(RelativeURLValidator, self).__init__()
        self.verify_exists = verify_exists
        self.user_agent = validator_user_agent

    def __call__(self, value):
        try:
            super(RelativeURLValidator, self).__call__(value)
        except ValidationError, e:
            # Trivial case failed. Try for possible IDN domain
            if value:
                value = smart_unicode(value)
                scheme, netloc, path, query, fragment = urlparse.urlsplit(value)
                try:
                    netloc = netloc.encode('idna') # IDN -> ACE
                except UnicodeError: # invalid domain part
                    raise e
                url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
                super(RelativeURLValidator, self).__call__(url)
            else:
                raise
        else:
            url = value

        if self.verify_exists:
            broken_error = ValidationError(
                _(u'This URL appears to be a broken link.'), code='invalid_link')

            if url.startswith('http://') or url.startswith('ftp://'):
                headers = {
                    "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
                    "Accept-Language": "en-us,en;q=0.5",
                    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                    "Connection": "close",
                    "User-Agent": self.user_agent,
                }
                url = url.encode('utf-8')
                try:
                    req = urllib2.Request(url, None, headers)
                    req.get_method = lambda: 'HEAD'
                    #Create an opener that does not support local file access
                    opener = urllib2.OpenerDirector()

                    #Don't follow redirects, but don't treat them as errors either
                    error_nop = lambda *args, **kwargs: True
                    http_error_processor = urllib2.HTTPErrorProcessor()
                    http_error_processor.http_error_301 = error_nop
                    http_error_processor.http_error_302 = error_nop
                    http_error_processor.http_error_307 = error_nop

                    handlers = [urllib2.UnknownHandler(),
                                urllib2.HTTPHandler(),
                                urllib2.HTTPDefaultErrorHandler(),
                                urllib2.FTPHandler(),
                                http_error_processor]
                    try:
                        import ssl
                        handlers.append(urllib2.HTTPSHandler())
                    except:
                        #Python isn't compiled with SSL support
                        pass
                    map(opener.add_handler, handlers)
                    if platform.python_version_tuple() >= (2, 6):
                        opener.open(req, timeout=10)
                    else:
                        opener.open(req)
                except ValueError:
                    raise ValidationError(_(u'Enter a valid URL.'), code='invalid')
                except: # urllib2.URLError, httplib.InvalidURL, etc.
                    raise broken_error

            else:
                # Resolve the relative URL
                try:
                    resolve(url)
                except Http404:
                    raise broken_error
