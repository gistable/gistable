class UserUpdateView(AuthenticatorViewMixin, UpdateView):
    model = User
    template_name = 'manager/authenticator/user_list.html'

    def get_form_class(self):
        return modelformset_factory(User, extra=0)

    def get_form_kwargs(self):
        kwargs = super(UserUpdateView, self).get_form_kwargs()
        kwargs['queryset'] = kwargs['instance']
        del kwargs['instance']
        return kwargs

    def get_object(self):
        return self.get_queryset()