""" Generate lovely ideas for hack day talks """

import random
import re

productions = {
    'tech': [
        'HTML5',
        'Audio',
        'CoffeeScript',
        'Twig',
        'jQuery',
        'memcached',
        'Mashups',
        'Backbone.js',
        'Bootstrap',
        'Lisp',
        'CSS3',
        'git',
        'Clojure',
        'Haskell',
        'Monads'
    ],

    'other': [
        'bacon',
        'chocolate',
        'Befunge',
        'Autotune',
        'dubstep'
    ],

    'person': [
        'goths',
        'dogs',
        'zombies'
    ],

    # pp = preposition phrase
    'pp': [
        'in 140 characters',
        'in small pieces',
        'on a Raspberry Pi',
        'for great justice',
        'FTW'
    ],

    'talk': [
        '${tech} for ${person}',
        '${tech} + ${tech} = awesome',
        '${tech} with ${other}',
        '${tech} and ${other}',
        '${tech} ${pp}',
        'How to use ${tech} to make an amazing mess',
    ]
}

def randomly_generated(nt):
    template = random.choice(productions[nt])
    def replace(match):
        return randomly_generated(match.group(1))
    return re.sub(r'\$\{(\w+)\}', replace, template)

def random_idea():
    return randomly_generated('talk')
