from pyparsing import *

# By default, PyParsing treats \n as whitespace and ignores it
# In our grammer, \n is significant, so tell PyParsing not to ignore it
ParserElement.setDefaultWhitespaceChars(" \t")

def parse(input_string):
    def convert_prop_to_dict(tokens):
        """Convert a list of field property tokens to a dict"""
        prop_dict = {}
        for token in tokens:
            prop_dict[token.property_key] = token.property_value
        return prop_dict

    # The form DSL grammar expressed in PyParsing notation
    # PyParsing has a brilliant DSL syntax
    word = Word(alphas)
    newline = Suppress("\n")
    colon = Suppress(":")
    arrow = Suppress("->")
    key = word.setResultsName("property_key")
    value = Word(alphanums).setResultsName("property_value")
    field_property = Group(key + colon + value).setResultsName("field_property")
    field_type = oneOf("CharField EmailField PasswordField").setResultsName("field_type")
    field_name = word.setResultsName("field_name")
    field = Group(field_name + colon + field_type + Optional(arrow + OneOrMore(field_property)).setParseAction(convert_prop_to_dict) + newline).setResultsName("form_field")
    form_name = word.setResultsName("form_name")
    form = form_name + newline + OneOrMore(field).setResultsName("fields")

    return form.parseString(input_string)

# Code to create an Internal DSL to make outputting HTML easy
class HtmlElement(object):
    """The base element used by all the other classes"""
    
    default_attributes = {} # If the element has any default attributes
    tag = "unknown_tag" # Name of the tag
    
    def __init__(self, *args, **kwargs):
        """Children are passed in as args, attributes as kwargs"""
        
        self.attributes = kwargs
        self.attributes.update(self.default_attributes)
        self.children = args

    def __str__(self):
        """Render the tag contents as HTML"""

        # Convert the attributes into HTML representation
        attribute_html = " ".join(["{}='{}'".format(name, value) for name,value in self.attributes.items()])
        
        if not self.children:
            # If there are no children, render in empty tag format
            return "<{} {}/>".format(self.tag, attribute_html)
        else:
            # Otherwise render an open tag, followed by the children, followed by close tag
            children_html = "".join([str(child) for child in self.children])
            return "<{} {}>{}</{}>".format(self.tag, attribute_html, children_html, self.tag)

class Form(HtmlElement):
    """Form tag"""
    
    tag = "form"

class Input(HtmlElement):
    """Input tag"""
    
    tag = "input"

    def __init__(self, *args, **kwargs):
        """The name parameter is compulary for input tags"""
        
        HtmlElement.__init__(self, *args, **kwargs)

        # If there is a label attribute, then store that and delete it
        # Otherwise use the name attribute for the label
        self.label = self.attributes["label"] if "label" in self.attributes else self.attributes["name"]
        if "label" in self.attributes:
            del self.attributes["label"]

    def __str__(self):
        """The string representation also renders the label tag"""
        label_html = "<label>{}</label>".format(self.label)
        return label_html + HtmlElement.__str__(self) + "<br/>"

class CharField(Input):
    """Char field"""
    
    default_attributes = {"type":"text"}

class EmailField(CharField):
    """Email field (same as CharField for now)"""
    pass

class PasswordField(Input):
    """Password field, set type='password' for this field"""
    
    default_attributes = {"type":"password"}

def render(form):
    """Render the parsed form into HTML"""

    # Map the field name string to a field class
    field_dict = {"CharField": CharField, "EmailField": EmailField, "PasswordField": PasswordField}

    # Create the field classes
    fields = [field_dict[field.field_type](name=field.field_name, **field[2]) for field in form.fields]

    # Create the form
    return Form(*fields, id=form.form_name.lower())

input_form = """UserForm
name:CharField -> label:Username size:25
email:EmailField -> size:32
password:PasswordField
"""

print render(parse(input_form))
