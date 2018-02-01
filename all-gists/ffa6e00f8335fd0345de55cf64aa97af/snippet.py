    def get(self, apiQueryURI, params=None, **kwargs):
        """
        Append the specified query URI to the base URL, which is then sent to the REST API.
        Results are returned as a requests.Response object.

        :param apiQueryURI: URI for the query, to be appended to the base URL
        :type apiQueryURI: str
        :return: requests.Response
        :rtype: requests.Response
        """
        print self.methodName() + '():', apiQueryURI

        apiQueryURIFormatted = apiQueryURI
        if (util.stringContainsAllCharacters(apiQueryURI, '{}')):
            try:
                apiQueryURIFormatted = apiQueryURI.format(**kwargs)
            except Exception as formattingException:
                message = \
                    'Error while formatting query, "%s", "%s: %s"' % \
                    (apiQueryURI, formattingException.__class__.__name__, formattingException.message)
                raise requests.RequestException(message)

        return self._sendRequest(self.methodName(), apiQueryURIFormatted, params=params, **kwargs)
