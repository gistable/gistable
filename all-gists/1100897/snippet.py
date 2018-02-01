class UserResource(ModelResource):
    def cached_obj_get(self, request=None, **kwargs):
        if request and 'id' in kwargs and kwargs['id'] == 'self':
            return request.user
        return super(UserResource, self).cached_obj_get(request, **kwargs)

    