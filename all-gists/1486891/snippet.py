"""
Django's SMTP EmailBackend doesn't support an SMTP_SSL connection necessary to interact with Amazon SES's newly announced SMTP server. We need to write a custom EmailBackend overriding the default EMailBackend's open(). Thanks to https://github.com/bancek/django-smtp-ssl for the example.
"""

--- settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'username'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True

--- shell

>>> from django.core.mail import send_mail
>>> send_mail('subject', 'message', 'from@example.com', ['to@example.com'])
SMTPServerDisconnected: Connection unexpectedly closed

--- settings.py

EMAIL_BACKEND = 'backends.smtp.SSLEmailBackend'

--- backends/smtp.py

import smtplib

from django.core.mail.utils import DNS_NAME
from django.core.mail.backends.smtp import EmailBackend

class SSLEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        try:
            self.connection = smtplib.SMTP_SSL(self.host, self.port,
                                           local_hostname=DNS_NAME.get_fqdn())
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except:
            if not self.fail_silently:
                raise

--- shell

>>> from django.core.mail import send_mail
>>> send_mail('subject', 'message', 'from@example.com', ['to@example.com'])
1
