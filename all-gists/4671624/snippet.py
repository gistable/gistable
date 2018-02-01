"""
Mark Allan B. Meriales

A command tool that generates fixture data (json) 
based from existing Models. This can be helpful when
doing testing.
"""

from django.core.management.base import BaseCommand
from django.db import models
from django.db.utils import DatabaseError

output_file = '/tmp/initial_data.json'
exclude_model = ['ContentType','Session']

class FixtureModel:
    name = None
	fields = []

	def __init__(self, model=None):
		if model:
			self.set_model(model)
			self.init_attributes()

	def init_attributes(self):
		self.set_name(self.model.__name__)
		self.set_fields()

	def set_model(self, model):
		self.model = model

	def set_name(self, modelname=None):
		self.name = modelname

	def set_fields(self):
		# need to re-initialize fields
		self.fields = []
		for field in self.model._meta.fields:
			self.fields.append(field.name)

	def generate_fixtures(self):
		"""
		returns json string
		"""
		ret_str = ''

		try:
			qs = self.model.objects.all()
			if qs.count():
				s_model = '"model":"%s.%s"' % (self.model._meta.app_label, self.model.__name__.lower())
				for q in qs:
					i_pk = '"pk": %d' % q.pk
					s_tmp = ''			
					for field in self.fields:
						if not field == 'id':
							try:
								val = getattr(q, field, '')
								# check if obj has an id attr (ForeignKey)
								val = getattr(val, 'id', val)
							except:
								pass
							if isinstance(val, (int, long)):
								s_tmp += '\n\t\t"%s":%d,' % (field, val)
							elif isinstance(val, float):
								s_tmp += '\n\t\t"%s":%f,' % (field, val)
							else:
								s_tmp += '\n\t\t"%s":"%s",' % (field, val)

					ret_str += '{\n\t%s,\n\t%s,\n\t"fields": {%s\n\t}\n},\n' % (s_model,i_pk,s_tmp[:-1])
		except DatabaseError as e:
			print e.message

		return ret_str


def write_to_file(str):
	f = open(output_file, 'w')
	f.write(str)
	f.close()


class Command(BaseCommand):
	"""
	Generate fixture from model(s).
	Usage:
	$ python manage.py Model1 ... ModelN
	or
	$ python manage.py ALL ExcludeModel1 ... ExcludedModelN
	"""

	def handle(self, *args, **kwargs):
		if len(args) < 1:
			print self.__doc__
			return False
		
		str = ''
		if args[0] == "ALL":
			if len(args) > 1:
				for arg in range(1, len(args)):
					exclude_model.append(args[arg])
			for model in models.get_models():
				if model.__name__ not in exclude_model:
					fixture_model = FixtureModel(model)
					str += fixture_model.generate_fixtures()
		else:
			for model in models.get_models():
				if model.__name__ in args:
					fixture_model = FixtureModel(model)
					str += fixture_model.generate_fixtures()
					if len(str):
						print model.__name__, "- done!!!"

		if str:
			write_to_file(str[:-2])
		else:
			print "No fixture created"