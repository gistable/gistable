"""
How Django generates SECRET_KEYs for new Django projects.

See:
https://github.com/django/django/blob/1.7.1/django/core/management/commands/startproject.py#L27
"""

from django.utils.crypto import get_random_string

# Create a random secret_key
chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
secret_key = get_random_string(50, chars)
