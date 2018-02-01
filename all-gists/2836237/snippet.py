# Example based on http://lukeplant.me.uk/blog/posts/djangos-cbvs-were-a-mistake/
# Not tested, just designed to give a general idea of the games CBVs let you play
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import ProcessFormView

# Utilities for interacting with a user
class UserViewMixin(object):
    _high_priority_user = None

    @property
    def high_priority_user(self):
        if self._high_priority_user is None:
            user = self.request.user
            self._high_priority = (not user.is_anonymous() and user.get_profile().high_priority)
        return self._high_priority_user

    def send_message(self, details):
        email = details['email']
        message = details['message']
        send_contact_message(email, message)
        if self.high_priority_user and details['urgent']:
             send_text_message(email, message)

    def get_contact_details(self):
        user = self.request.user
        if user.is_anonymous():
            return {}
        return {'email' : user.email}


# Put custom mixins first, since we can ensure they play nice with multiple inheritance
class ContactView(UserViewMixin, ProcessFormView):
    template_name = 'contact.html'
    success_url = reverse_lazy('contact_thanks')

    def get_form_class(self):
        return HighPriorityContactForm if self.high_priority_user else ContactForm

    def get_initial(self):
        initial = super(ContactView, self).get_initial()
        initial.update(self.get_contact_details())
        return initial

    def form_valid(self, form):
        self.send_message(form.cleaned_data)
        return super(ContactView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        context['high_priority_user'] = self.high_priority_user
        return context