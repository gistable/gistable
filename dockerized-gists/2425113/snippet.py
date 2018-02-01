#!/bin/env python2.7
'''This module loads the Jimmy John's menu from their website and provides
you with a random selection from their main (numbered) sandwich menu.
Recommended usage is to just run it as a script.
'''

from BeautifulSoup import BeautifulSoup
import requests
import random
import re

ATTRACT_MODE = ['Your sandvich is the %s',
                'You know you want a %s',
                'This one looks fine... %s',
                'Desk-Ramen is bad for you: %s',
                'This one delivers itself, promise! %s',
                ]

def jimmy_johns():
    '''Get JJ's menu and return a random selection as a dictionary
    of sandwich number, name and description.

    Only gets numbered sandwiches because getting the huge or tiny ones
    at random is too surprising. Also it's hard to maintain the element of
    surprise when there is no number.
    '''

    menu = requests.get('http://jimmyjohns.com/menu/menu.aspx').content
    soup = BeautifulSoup(menu, convertEntities=BeautifulSoup.HTML_ENTITIES)

    _pattern = re.compile(r'#(\d*) (.*)')

    sandwiches = []
    for sandwich in soup.findAll('dd'):
        for sandwich_name in sandwich.findAll('a'):
            full_name = sandwich_name.text
            if "#" in full_name:
                # Probably a numbered sammich
                number = _pattern.search(full_name).group(1)

                # Strip the number off of the name
                name = _pattern.search(full_name).group(2)

                #The description has the name in it, so remove it.
                description = sandwich.text.replace(full_name, '')

                sandwiches.append({'number': number, 'name': name,
                                   'description': description})

    return random.choice(sandwiches)

def main():
    '''Get our sammich and format it nicely.
    Returns a string.'''
    sammich = jimmy_johns()
    desc = "\n #%(number)s %(name)s: %(description)s" % sammich
    message = random.choice(ATTRACT_MODE) % desc
    return message

if __name__ == "__main__":
    print main()