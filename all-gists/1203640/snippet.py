from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.defaultfilters import striptags

def send_mail(subject, html_message, from_email, recipient_list, fail_silently=False, connection=None):
    text_message = striptags(html_message)
    recipient_list = getattr(settings, 'EMAIL_RECIPIENTS_OVERRIDE', recipient_list)

    msg = EmailMultiAlternatives(subject, text_message, from_email, recipient_list, connection=connection)
    msg.attach_alternative(html_message, "text/html")
    msg.send(fail_silently=fail_silently)