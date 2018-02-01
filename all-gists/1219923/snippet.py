# template tag: {% url django.contrib.auth.views.password_reset_confirm uidb36=uidb36 token=token %}
from django.utils.http import int_to_base36
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User


user = User.objects.get(pk=1)
context = {
    'uidb36': int_to_base36(user.pk),
    'token' = default_token_generator.make_token(user),    
 }