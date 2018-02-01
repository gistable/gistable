from django.contrib.sessions.models import Session
for s in Session.objects.iterator():
    session_dict = s.get_decoded()
    if '_auth_user_backend' in session_dict.keys():
        #New backend is social.backends.facebook.FacebookOAuth2
        #Change from old backend
        if session_dict['_auth_user_backend'] == 'social_auth.backends.facebook.FacebookBackend':
            session_dict['_auth_user_backend'] = 'social.backends.facebook.FacebookOAuth2'
            new_s = Session.objects.save(s.session_key, session_dict, s.expire_date)
            print new_s.pk

