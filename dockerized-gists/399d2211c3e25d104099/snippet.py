from __future__ import unicode_literals
from collections import defaultdict
import random
import requests
from graphviz import Digraph

USERNAME = 'shauns'

PASSWORD = '****'

REPO_OWNER = 'shauns'

REPO_NAME = '****'

pulls = []

auth = (USERNAME, PASSWORD)

root_url = 'https://api.github.com/repos/{}/{}/pulls'.format(
    REPO_OWNER, REPO_NAME
)

pull_params = {'status': 'open'}

res = requests.get(root_url, auth=auth, params=pull_params)

pulls.extend(res.json())

while res.links.get('next'):
    next_url = res.links['next']['url']
    res = requests.get(next_url, auth=auth, params=pull_params)
    pulls.extend(res.json())

# print pulls

pr_details = {}

for pull in pulls:
    pr_details[pull['id']] = {
        'title': pull['title'],
        'author': pull['user']['login'],
        'head': pull['head']['ref'],
        'base': pull['base']['ref'],
    }

print pr_details

dot = Digraph('GH', graph_attr={
    'overlap': 'true', 'ranksep': '2', 'ratio': '0.5'})

colours = [
    '#ff0000', '#00ff00', '#0000ff',
    '#ffff00', '#ff00ff', '#00ffff',
    '#ff6666', '#66ff66', '#6666ff',
    '#ffff66', '#ff66ff', '#66ffff',
]


def new_colour():
    colour = random.choice(colours)
    colours.remove(colour)
    return colour


author_colours = defaultdict(new_colour)

for pr_id, pull in pr_details.items():
    pr_id_str = str(pr_id)
    dot.node(
        pr_id_str, '{} (@{})'.format(pull['title'], pull['author']),
        _attributes={'shape': 'box', 'style': 'filled',
                     'fillcolor': author_colours[pull['author']]}
    )
    dot.node(
        pull['head'], _attributes={
            'style': 'filled',
            'fillcolor': '#ffffff',
        }
    )
    dot.node(
        pull['base'], _attributes={
            'style': 'filled',
            'fillcolor': '#ffffff',
        }
    )
    dot.edge(
        pull['base'], pr_id_str
    )
    dot.edge(
        pr_id_str, pull['head']
    )

# Run this through dot -Tpng -o x.png -Ktwopi x.dot
print dot
