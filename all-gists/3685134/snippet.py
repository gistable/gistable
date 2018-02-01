import re
from django import forms
from django.db import models

class ColourFormField(forms.IntegerField):
	default_error_messages = {
		'invalid': 'Enter a valid colour value: e.g. "#ff0022"',
	}
	
	def __init__(self, *args, **kwargs):
		super(ColourFormField, self).__init__(*args, **kwargs)
	
	def clean(self, value):
		if value == '' and not self.required:
			return u''

		if not re.match('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
			raise forms.ValidationError(self.error_messages['invalid'])
		
		value = int(value[1:], 16)

		super(ColourFormField, self).clean(value)

		return value

class ColourField(models.PositiveIntegerField):

	description = "HEX value for a colour"

	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = 6
		super(ColourField, self).__init__(*args, **kwargs)

	def to_python(self, value):
		super(ColourField, self).to_python(value)

		try:
			string = hex(value)[2:]

			if string == "0":
				string = "000000"

			return "#"+string.upper()
		except TypeError:
			return None
		
	def get_prep_value(self, value):
		try:
			# hex to int, save the int representation of the colour hex code to the database
			return value
		except ValueError:
			return None

	def formfield(self, *args, **kwargs):
		kwargs['form_class'] = ColourFormField

		return super(ColourField, self).formfield(*args, **kwargs)