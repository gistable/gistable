# utils.py
import json
from django.contrib.postgres.forms.jsonb import InvalidJSONInput, JSONField


class ReadableJSONFormField(JSONField):
    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        return json.dumps(value, ensure_ascii=False, indent=4)


      
# admin.py
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from .utils import ReadableJSONFormField


@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'form_class': ReadableJSONFormField},
    }
