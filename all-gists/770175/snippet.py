class SiteResource(ModelResource):
    """ Thing that are meant to be accessed with a cookie """

    def dispatch(self, request_type, request, **kwargs):
        kwargs['site'] = Site.objects.get_current()
        return super(SiteResource, self).dispatch(request_type, request, **kwargs)
