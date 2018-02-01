"""
Example of mandrill service in python (http://mandrill.com/)

Description of usage in python:
Russian: http://www.lexev.org/2014/send-email-django-project-mandrill-service/
English: http://www.lexev.org/en/2014/send-email-django-project-mandrill-service/
"""

# ======
# Django
# ======

# install
# -------
pip install django-mandrill

# settings.py
# -----------
INSTALLED_APPS += ('django_mandrill',)
EMAIL_BACKEND = 'django_mandrill.mail.backends.mandrillbackend.EmailBackend'
MANDRILL_API_KEY = "valid api key"

# mandrill_mail.py
# ----------------
from django_mandrill.mail import MandrillTemplateMail


def send_mandrill_email(template_name, email_to, context=None, curr_site=None):
    if context is None:
        context = {}
    message = {
        'to': [],
        'global_merge_vars': []
    }
    for em in email_to:
        message['to'].append({'email': em})

    for k, v in context.items():
        message['global_merge_vars'].append(
            {'name': k, 'content': v}
        )
    MandrillTemplateMail(template_name, [], message).send()


send_mandrill_email('template-1', ["sendto@email.com"], context={'Name': "Bob Marley"})


# ================
# Standalone usage
# ================

# install
# -------
pip install mandrill

# send email
# ----------
import mandrill

API_KEY = 'valid_api_key'


def send_mail(template_name, email_to, context):
    mandrill_client = mandrill.Mandrill(API_KEY)
    message = {
        'to': [],
        'global_merge_vars': []
    }
    for em in email_to:
        message['to'].append({'email': em})

    for k, v in context.iteritems():
        message['global_merge_vars'].append(
            {'name': k, 'content': v}
        )
    mandrill_client.messages.send_template(template_name, [], message)

send_mail('template-1', ["sendto@email.com"], context={'Name': "Bob Marley"})
