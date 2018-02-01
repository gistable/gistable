#!/usr/bin/env python

from random import choice
from string import ascii_lowercase, ascii_uppercase, digits
from sys import argv

VOWELS = ['a', 'e', 'i', 'o', 'u']
CONSONANTS = [l for l in ascii_lowercase if l not in VOWELS]
FIRST = choice([l for l in ascii_uppercase if l.lower() not in VOWELS])

def generate_password(length):
    """
    Generate a random, but somewhat readable password.
    """
    random_password = [FIRST]
    
    for i in range(length - 2):
        if i % 2:
            random_password.append(choice(CONSONANTS))
        else:
            random_password.append(choice(VOWELS))
    
    random_password.append(choice(digits))
    return "".join(random_password)
    
if __name__ == '__main__':
    try:
        password_length = int(argv[1])
    except IndexError:
        password_length = 8
    
    print generate_password(password_length)
