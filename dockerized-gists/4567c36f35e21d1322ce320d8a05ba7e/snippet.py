class JSON:
    def __init__(self):
        import re
        from dateutil.parser import parse
        from django.db.models import Model
        from django.apps import apps

        pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})?(T)?(\d{2}:\d{2}:\d{2}(?:\.\d{6})?(?:[+-]\d{2}:\d{2})?)?$')

        def model_decoder(o):
            model = o.pop('@model', None)
            if model is None: return None, False

            val = o.pop('@value', None)
            if model is None: return None, False

            return ModelDict(apps.get_model(model)).from_dict(val), True

        def datetime_decoder(o):
            val = o.get('@value', None)
            if val is None: return None, False

            match = pattern.match(val)
            if match is None: return None, False

            dat, sep, tim = [(v is not None) for v in match.groups()]
            if (not (dat or tim or sep)) or (dat and tim and (not sep)):
                return None, False

            try:
                res = parse(val)
            except ValueError as e:
                return None, False

            if not dat:
                res = res.time()
            elif not tim:
                res = res.date()

            return res, True

        decoders = dict(model= model_decoder, datetime= datetime_decoder)

        def decoder(val, hook):
            if not isinstance(val, dict): return hook(val)

            typ = val.get('@type', None)
            if typ is None: return hook(val)

            handler = decoders.get(typ, None)
            if handler is None: return hook(val)

            res, ok = handler(val)
            if ok: return res

            return hook(val)

        def encoder(obj):
            if hasattr(obj, 'isoformat'):
                res = {
                    '@type': 'datetime',
                    '@value': obj.isoformat(),
                }

                return res, True
            elif isinstance(obj, Model):
                model = type(obj)
                obj = ModelDict(model).to_dict(obj)

                res = {
                    '@type': 'model',
                    '@model': '%s.%s' % (model._meta.app_label, model.__name__),
                    '@value': obj,
                }

                return res, True

            return None, False

        self._encoder = encoder
        self._decoder = decoder

    def dump(self,
             obj,
             fp,
             skipkeys=False,
             ensure_ascii=True,
             check_circular=True,
             allow_nan=True,
             cls=None,
             *args,
             **kwargs):
        from json import dump, JSONEncoder

        if cls is None: cls = JSONEncoder

        class encoder(cls):
            def default(this, obj):
                res, ok = self._encoder(obj)
                if ok: return res

                return super(encoder, this).default(obj)

        dump(obj, fp, skipkeys, ensure_ascii, check_circular, allow_nan, encoder, *args, **kwargs)

    def dumps(self,
              obj,
              skipkeys=False,
              ensure_ascii=True,
              check_circular=True,
              allow_nan=True,
              cls=None,
              *args,
              **kwargs):
        from json import dumps, JSONEncoder

        if cls is None: cls = JSONEncoder

        class encoder(cls):
            def default(this, obj):
                res, ok = self._encoder(obj)
                if ok: return res

                return super(encoder, this).default(obj)

        res = dumps(obj, skipkeys, ensure_ascii, check_circular, allow_nan, encoder, *args, **kwargs)

        if ensure_ascii:
            res = res.encode()

        return res

    def load(self, fp, cls= None, object_hook= None, *args, **kwargs):
        from json import load

        if object_hook is None: object_hook = lambda o: o

        return load(fp, cls, lambda o: self._decoder(o, object_hook), *args, **kwargs)

    def loads(self, s, encoding= None, cls= None, object_hook= None, *args, **kwargs):
        from json import loads

        if object_hook is None: object_hook = lambda o: o

        if isinstance(s, bytes):
            if encoding is None:
                s = s.decode()
            else:
                s = s.decode(encoding= encoding)

        return loads(s, None, cls, lambda o: self._decoder(o, object_hook), *args, **kwargs)


class ModelDict(object):
    def __init__(self, model):
        self._model = model

    def to_dict(self, instance, fields= None, exclude= None):
        from django.db.models.fields.related import ManyToManyField, ForeignObjectRel

        opts = self._model._meta
        data = {}

        for f in opts.get_fields():
            if (fields and (f.name not in fields)) or (exclude and (f.name in exclude)):
                continue

            if isinstance(f, ForeignObjectRel):
                continue

            if isinstance(f, ManyToManyField):
                if not f.rel.through._meta.auto_created:
                    continue

                if instance.pk is None:
                    data[f.name] = []
                else:
                    # MultipleChoiceWidget needs a list of pks, not object instances.
                    qs = f.value_from_object(instance)

                    if qs._result_cache is not None:
                        data[f.name] = [item.pk for item in qs]
                    else:
                        data[f.name] = list(qs.values_list('pk', flat=True))
            else:
                data[f.name] = f.value_from_object(instance)

        return data

    def from_dict(self, data, fields= None, exclude= None):
        from django.db.models.fields.related import ManyToManyField, RelatedField, ForeignObjectRel
        from django.db.models import FileField

        opts = self._model._meta
        instance = self._model()

        file_field_list = []

        for f in opts.get_fields():
            if (f.name not in data) or (fields and (f.name not in fields)) or (exclude and (f.name in exclude)):
                continue

            if isinstance(f, ForeignObjectRel):
                continue

            # Defer saving file-type fields until after the other fields, so a
            # callable upload_to can use the values from other fields.
            if isinstance(f, FileField):
                file_field_list.append(f)
            else:
                value = data[f.name]
                if isinstance(f, RelatedField):
                    def get_related_value(pk):
                        try:
                            if pk is not None:
                                return f.related_model.objects.get(pk= pk)
                        except:
                            pass

                        return None

                    if isinstance(f, ManyToManyField):
                        if not f.rel.through._meta.auto_created:
                            continue

                        value = [ o for o in (get_related_value(v) for v in value) if o is not None ]
                    else:
                        value = get_related_value(value)

                if value is not None:
                    try:
                        f.save_form_data(instance, value)
                    except:
                        pass

        for f in file_field_list:
            f.save_form_data(instance, instance[f.name])

        if instance.pk is not None:
            instance._state.adding = False

        return instance
