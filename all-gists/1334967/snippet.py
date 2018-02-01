class MobileWebsiteMiddleware(object):

    MOBILE_PREFIX = '/m/'
    MOBI_REG = re.compile(
        '(iphone|windows ce|mobile|phone|symbian|mini|pda|ipod|mobi|blackberry|playbook|vodafone|kindle)',
        re.IGNORECASE)

    def process_request(self, request):

        if 'HTTP_USER_AGENT' in request.META:
            userAgent = request.META.get('HTTP_USER_AGENT')
            matches = self.MOBI_REG.search(userAgent)
            path = request.path_info

            if matches:
                # from mobile browser, check if need to redirect to mobile
                if not path.startswith(self.MOBILE_PREFIX):
                    # need to redirect to mobile version
                    return HttpResponseRedirect('/m' + path)
            elif path.startswith(self.MOBILE_PREFIX):
                    # need to redirect to normal version
                    return HttpResponseRedirect(path[2:])

        return None