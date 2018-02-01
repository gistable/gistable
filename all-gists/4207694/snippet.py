>>> from jinja2 import Template
>>> tmpl = """{% if name != "Jeff" %}Nothing to see here move along{% else %}
... hello {{name}}, how are you?{% endif %}"""
>>> template = Template(tmpl)
>>> print template.render({"name": "Jeff"})

hello Jeff, how are you?
>>> print template.render({"name": "John"})
Nothing to see here move along
>>> 