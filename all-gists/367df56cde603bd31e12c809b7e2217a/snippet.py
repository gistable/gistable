from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction


class InvalidInputsError(Exception):

    def __init__(self, errors, non_field_errors):
        self.errors = errors
        self.non_field_errors = non_field_errors

    def __str__(self):
        return f'{repr(self.errors)} {repr(self.non_field_errors)}'


class Service(forms.Form):

    def service_clean(self):
        if not self.is_valid():
            raise InvalidInputsError(self.errors, self.non_field_errors())

    @classmethod
    def execute(cls, inputs, files=None, **kwargs):
        instance = cls(inputs, files, **kwargs)
        instance.service_clean()
        with transaction.atomic():
            return instance.process()

    def process(self):
        raise NotImplementedError()


class MultipleFormField(forms.Field):
    """
    A field that contains many forms, similar to a FormSet but easier to clean
    """

    def __init__(self, form_class, min_count=1, max_count=None, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.form_class = form_class
        self.min_count = min_count
        self.max_count = max_count

    def clean(self, values):
        if len(values) < self.min_count:
            raise ValidationError(
                f'There needs to be at least {self.min_count} item/s.')

        if self.max_count and len(values) > self.max_count:
            raise ValidationError(
                f'There needs to be at most {self.max_count} item/s.')

        item_forms = []
        for index, item in enumerate(values):
            item_form = self.form_class(item)
            if not item_form.is_valid():
                raise ValidationError(f'[{index}]: {repr(item_form.errors)}')
            item_forms.append(item_form)

        return item_forms
