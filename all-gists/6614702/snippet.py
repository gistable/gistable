# http://stackoverflow.com/questions/8702772/django-get-list-of-models-in-application
from django.db.models import get_app, get_models

app = get_app('my_application_name')

for model in get_models(app):
    new_object = model() # Create an instance of that model
    model.objects.filter(...) # Query the objects of that model
    model._meta.db_table # Get the name of the model in the database
    model._meta.verbose_name # Get a verbose name of the model
    # ...