from random import choice
from string import ascii_lowercase, digits
from django.contrib.auth.models import User

def generate_random_username(length=16, chars=ascii_lowercase+digits, split=4, delimiter='-'):
    
    username = ''.join([choice(chars) for i in xrange(length)])
    
    if split:
        username = delimiter.join([username[start:start+split] for start in range(0, len(username), split)])
    
    try:
        User.objects.get(username=username)
        return generate_random_username(length=length, chars=chars, split=split, delimiter=delimiter)
    except User.DoesNotExist:
        return username;
