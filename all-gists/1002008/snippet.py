class YourAdmin(ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        ref = request.META.get('HTTP_REFERER','')
        path = request.META.get('PATH_INFO','')
        if not ref.split(path)[-1].startswith('?'):
            q = request.GET.copy()
            q['usertype'] = 'Publisher'
            q['user_status__exact'] = 'activated'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(BulkMigrationAdmin,self).changelist_view(request, extra_context=extra_context)
