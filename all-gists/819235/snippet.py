from django.views.generic.edit import FormView
from django.views.generic.base import RedirectView

from registration.models import RegistrationProfile
from forms import RegistrationForm

class AccountRegistrationView(FormView):
    
    template_name = 'authentication/registration_form.html'
    form_class = RegistrationForm
    url = lazy_reverse('core:core-welcome')

    extra_context = {
        'page_robots': u'INDEX, NOFOLLOW',
        'page_description': u'Napravi novi nalog',
        'page_keywords': u'registracija, registriranje, novi nalog, napravi nalog',
    }
          
    def form_valid(self, form):
        AccountRegistrationView.register_user(self.request, **form.cleaned_data)
       
        return super(AccountRegistrationView, self).form_valid(self, form)
            
    def get_context_data(self, **kwargs):
        context = super(AccountRegistrationView, self).get_context_data(**kwargs)
        
        context.update(self.extra_context)
        return context
    
    @classmethod
    def register_user(cls, request, **kwargs):
        '''
        Given an email address and password, create a new
        user account, which will initially be inactive.
        '''
        
        email, password = kwargs['email'], kwargs['password1']       
        user = cls.create_unique_user(email, password)
        
        cls.user_registered(user, request)
    
    @classmethod        
    def user_registered(cls, user, request):
        '''
        Handles successful user registrations.
        
        Creates a registration success messages and sends 
        a registration success email to the user.
        '''
        
        activation_key = RegistrationProfile.objects.get(user=user).activation_key
        context = {}
        
        messages.success(request,
                         _(u'Uspješno je napravljen novi nalog! '
                           u'Provjeri svoj inbox, poslali smo ti email na %s ' 
                           u'sa linkom da potvrdiš email i aktiviraš svoj nalog.' % user.email))
        
        context['user'] = user
        context['verification_url'] = (settings.SITE_ROOT + 
                                       reverse('authentication:auth-activate', 
                                               kwargs=dict(activation_key=activation_key)))
        
        user_email(user, _('Zdravo!'),
                   'authentication/email_registration_success.txt',
                   'authentication/email_registration_success.html',
                   context)
        
    @classmethod
    def create_unique_user(cls, email, password):
        '''
        Creates a unique user. Later, I'll burn in hell for this.
        '''

        create_inactive_user = RegistrationProfile.objects.create_inactive_user

        if Site._meta.installed: #@UndefinedVariable
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        try:
            username = uuid.uuid1().hex[:30]
            user = create_inactive_user(username, email, password, site, send_email=False)

            return user
        except IntegrityError:
            return cls.create_unique_user(email, password)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active:
            # Redirect registered users
            return HttpResponseRedirect(reverse('submissions:submissions-submission-list'))
        else:
            return super(AccountRegistrationView, self).dispatch(request, *args, **kwargs)


class AccountActivationView(RedirectView):
    
    url = lazy_reverse('core:core-welcome')
    
    def get(self, request, activation_key=None, *args, **kwargs):
        activated = RegistrationProfile.objects.activate_user(activation_key)
        
        if activated:
            messages.success(request, _(u'Super! Tvoj nalog je sada aktivan i možes se njim prijaviti.'))
        else:
            messages.error(request, 
                           _(u'Hej, nismo našli tvoj nalog! ' 
                             u'Provjeri još jednom link za aktiviraje naloga.'))
        
        return super(AccountActivationView, self).get(request, *args, **kwargs)

