from pprint import pprint
import jinja2
import markdown

HTML_TEMPLATE = """{% macro get_html() %}
{{ content | markdown }}
{% endmacro %}
{% set html_content = get_html() %}

Title from Markdown meta-data: {{ get_title() }}

{{ html_content }}
"""

MARKDOWN_WITH_METADATA = """Title: Hello world!

Header:
-------
*Markdown content*
"""

md = markdown.Markdown(extensions=['meta'])

env = jinja2.Environment()
env.filters['markdown'] = lambda text: jinja2.Markup(md.convert(text))
env.globals['get_title'] = lambda: md.Meta['title'][0]
env.trim_blocks = True
env.lstrip_blocks = True

print(env.from_string(HTML_TEMPLATE).render(content=MARKDOWN_WITH_METADATA))

print('title meta-data is retrieved from the content:')
pprint(md.Meta['title'])
