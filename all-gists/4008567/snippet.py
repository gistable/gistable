from urlparse import urlsplit, urlunsplit

from storages.backends.s3boto import S3BotoStorage


class ProtocolRelativeS3BotoStorage(S3BotoStorage):
    """Extends S3BotoStorage to return protocol-relative URLs

    See: http://paulirish.com/2010/the-protocol-relative-url/
    """
    def url(self, name):
        """Modifies return URLs to be protocol-relative."""
        url = super(ProtocolRelativeS3BotoStorage, self).url(name)
        parts = list(urlsplit(url))
        parts[0] = ''
        return urlunsplit(parts)
