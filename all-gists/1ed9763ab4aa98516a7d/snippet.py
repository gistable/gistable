from optparse import make_option

from django.core import serializers
from django.db.models import get_app, get_models


__author__ = 'mikhailturilin'

from django.core.management.base import BaseCommand


def get_foreign_key_fields(model):
    for field in model._meta.fields:
        if field.get_internal_type() == "ForeignKey":
            yield field


def model_name(model):
    return model._meta.object_name



def copy_instance(model, instance, from_database, to_database, ignore_errors=False, natural_key_models=None,
                  skip_models=None):
    if model_name(model) in (skip_models or []):
        return

    use_natural_keys = model_name(model) in (natural_key_models or [])

    if model.objects.using(to_database).filter(pk=instance.pk).exists():
        # print "Skipping %s:%s" % (model.__name__, obj.pk)
        return

    print "Copying %s:%s" % (model.__name__, instance.pk)


    # copy foreign keys
    for fk_field in get_foreign_key_fields(model):
        fk_obj = getattr(instance, fk_field.name, None)
        if fk_obj:
            copy_instance(fk_field.rel.to, fk_obj, from_database, to_database, ignore_errors)

    # copy m2m keys
    meta = model._meta
    for m2m in meta.many_to_many:
        # store many-to-many related objects for every
        # many-to-many relation of this object
        m2m_qs = getattr(instance, m2m.name)
        foreign_objs = m2m_qs.all()
        for m2m_obj in foreign_objs:
            copy_instance(m2m.rel.to, m2m_obj, from_database, to_database, ignore_errors)

    # copy itself
    original_data_json = serializers.serialize("json", [instance], use_natural_keys=use_natural_keys)
    print original_data_json

    new_data = serializers.deserialize("json", original_data_json, using=to_database)

    for n in new_data:
        try:
            n.save(using=to_database)
        except Exception as ex:
            if ignore_errors:
                print ex
            else:
                raise ex


def copy_model(model, from_database, to_database, ignore_errors=False, natural_key_models=None, skip_models=None):
    if model_name(model) in (skip_models or []):
        print "Skipping model %s" % model_name(model)
        return


    count = model.objects.using(from_database).count()
    print "%s objects in model %s" % (count, model_name(model))

    for obj in model.objects.using(from_database).all():
        copy_instance(model, obj, from_database, to_database, ignore_errors, natural_key_models, skip_models)


def flush_model(model, database):
    print "deleting all models '%s' in database '%s'" % (model.__name__, database)
    model.objects.using(database).delete()


def get_encoded_models(name):
    model_name = None
    if ':' in name:
        app_name, model_name = name.split(':')
    else:
        app_name = name

    app = get_app(app_name)

    models = get_models(app)

    if model_name:
        models = [model for model in models if model._meta.object_name == model_name]

    return models


class Command(BaseCommand):
    args = '<from_database to_database application1, application2 ...>'
    help = 'copies models between databases'

    option_list = BaseCommand.option_list + (
        make_option('--delete',
                    action='store_true',
                    dest='delete',
                    default=False,
                    help='Delete the models in the target db first'),
        make_option('--ignore-errors',
                    action='store_true',
                    dest='ignore-errors',
                    default=False,
                    help='Ignore save errors, just show them in the output'),

        make_option('--natural-key-models',
                    dest='natural-key-models',
                    default='',
                    help='List of the models names to use with natural key serialization'),

        make_option('--skip-models',
                    dest='skip-models',
                    default='',
                    help='List of the models names to skip'),
    )

    def handle(self, from_database, to_database, *args, **options):
        apps_names = args
        skip_models = options['skip-models'].split(',')
        natural_key_models = options['natural-key-models'].split(',')

        if options['delete']:
            for name in apps_names:
                for model in get_encoded_models(name):
                    print "Clearing model '%s'" % model.__name__
                    flush_model(model, to_database)

        for name in apps_names:
            models = get_encoded_models(name)
            for model in models:
                # import pudb; pu.db
                print "Copying model '%s'" % model.__name__
                copy_model(model, from_database, to_database, ignore_errors=options['ignore-errors'],
                           natural_key_models=natural_key_models, skip_models=skip_models)



