from django.core import serializers

from django.db.models import get_app, get_models
from django.db.models.query import QuerySet

def export_filer_models(output_file=None):
    """
    Exports filer models to output_file.
    """
    app = get_app('filer')
    model_list = get_models(app)
    # We handle filer differently because django-polymorphic interferes when serializing.
    def get_objects():
        for model in model_list:
            # Hack because of django-polyporphic D:<
            model.objects.queryset_class = QuerySet
            for obj in model.objects.iterator():
                yield obj
    serializers.serialize('json', get_objects(), indent=2, use_natural_keys=True, stream=output_file)
