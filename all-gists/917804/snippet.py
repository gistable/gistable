class UserResource(ModelResource):
    def dispatch_detail(request, **kwargs):
        if kwargs.get('pk') == "self":
            # This assumes that self.is_authenticated sets request.user
            self.is_authenticated(request)
            kwargs['pk'] = request.user.id
            return CurrentUserResource.dispatch_detail(request, **kwargs)
        return super(UserResource, self).dispatch_detail(request, **kwargs)

    

    