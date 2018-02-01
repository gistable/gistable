import sys
import markdown
import yaml
import os
from jinja2 import Environment, FileSystemLoader

with open(sys.argv[2], 'r') as f:
    content = yaml.safe_load(f.read())

for k in content:
    if k.startswith('md_'):
        content[k] = markdown.markdown(content[k])

tpath = os.path.join(os.getcwd(), 'templates')
env = Environment(loader=FileSystemLoader(tpath))
template = env.get_template(sys.argv[1])

print(template.render(content))

# example usage
#
# $ cat templates/foo.html
# <h1>{{ non_markdown_entry }}</h1>
# {{ md_items }}
# $ cat content/foo.yaml
# non_markdown_entry: 'Hey!'
# md_items: |
#     * item 1
#     * item 2
# $ python this_script.py foo.html content/foo.yaml >bar.html