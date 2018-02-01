from jinja2 import Template
text = """
hi
"""
template = Template(text)
template.render()  # passing variables here to the text template if needed