# -*- coding: utf-8 -*-
#!/usr/bin/env python

import warnings
from django.core.serializers.json import Serializer
from django.utils.encoding import smart_text, is_protected_type
from django.utils import six
from django.utils.html import escape


class JsonPropertySerializer(Serializer):
	def serialize(self, queryset, **options):
		"""
		Serialize a queryset.
		"""
		self.options = options

		self.stream = options.pop("stream", six.StringIO())
		self.selected_fields = options.pop("fields", None)
		self.use_natural_keys = options.pop("use_natural_keys", False)
		if self.use_natural_keys:
			warnings.warn("``use_natural_keys`` is deprecated; use ``use_natural_foreign_keys`` instead.", PendingDeprecationWarning)
		self.use_natural_foreign_keys = options.pop('use_natural_foreign_keys', False) or self.use_natural_keys
		self.use_natural_primary_keys = options.pop('use_natural_primary_keys', False)

		self.start_serialization()
		self.first = True
		for obj in queryset:
			self.start_object(obj)
			# Use the concrete parent class' _meta instead of the object's _meta
			# This is to avoid local_fields problems for proxy models. Refs #17717.
			concrete_model = obj._meta.concrete_model
			for field in concrete_model._meta.local_fields:
				if field.serialize:
					if field.rel is None:
						if self.selected_fields is None or field.attname in self.selected_fields:
							self.handle_field(obj, field)
					else:
						if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
							self.handle_fk_field(obj, field)
			for field in concrete_model._meta.many_to_many:
				if field.serialize:
					if self.selected_fields is None or field.attname in self.selected_fields:
						self.handle_m2m_field(obj, field)
			# Add to make possible to serialize via json property from a object!
			for name, field in obj.__class__.__dict__.iteritems():
				if isinstance(field, property):
					self.handle_property_field(obj, name)
			self.end_object(obj)
			if self.first:
				self.first = False
		self.end_serialization()
		return self.getvalue()

	def get_dump_object(self, obj):
		current = {key: item if isinstance(item, dict) else escape(item) for key, item in self._current.items()}
		return dict({"pk": smart_text(obj._get_pk_val(), strings_only=True), "model": smart_text(obj._meta)}.items() + current.items())

	def handle_field(self, obj, field):
		value = field._get_val_from_obj(obj)
		# Protected types (i.e., primitives like None, numbers, dates,
		# and Decimals) are passed through as is. All other values are
		# converted to string first.
		if is_protected_type(value):
			self._current[field.name] = value
		else:
			# Changed to make it possible to get the value from a choice field, the LABEL value!!
			value = field.value_to_string(obj)
			if len(field.choices) > 0:
				# Get the first value founded!
				value = filter(None, map(lambda x: x[1] if str(x[0]) == value else None, field.choices))
				if value:
					value = value[0]
			self._current[field.name] = value

	def handle_property_field(self, obj, name):
		self._current[name] = getattr(obj, name)
