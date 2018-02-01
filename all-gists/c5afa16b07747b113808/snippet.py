# https://stackoverflow.com/questions/25136282/what-is-the-right-way-to-extend-the-username-field-length-in-django-1-5

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    pass

USERNAME_LENGTH = 50
MyUser._meta.get_field('username').max_length = USERNAME_LENGTH
MyUser._meta.get_field('username').validators[0].limit_value = USERNAME_LENGTH
MyUser._meta.get_field('username').validators[1].limit_value = USERNAME_LENGTH
UserCreationForm.base_fields['username'].max_length = USERNAME_LENGTH
UserCreationForm.base_fields['username'].validators[0].limit_value = USERNAME_LENGTH