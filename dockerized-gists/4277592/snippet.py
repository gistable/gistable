import mongoengine
class MongoModelSerializer(serializers.ModelSerializer):

    def get_default_fields(self):
        cls = self.opts.model
        opts = get_concrete_model(cls)
        #pk_field = opts.pk
        fields = []
        fields += [getattr(opts, field) for field in opts._fields]
        #fields += [field for field in opts.many_to_many if field.serialize]

        ret = SortedDict()
        nested = bool(self.opts.depth)

        for model_field in fields:
            if model_field.primary_key:
                field = self.get_pk_field(model_field)

            else:
                field = self.get_field(model_field)

            if field:
                field.initialize(parent=self, field_name=model_field.name)
                ret[model_field.name] = field

        for field_name in self.opts.read_only_fields:
            assert field_name in ret,\
            "read_only_fields on '%s' included invalid item '%s'" %\
            (self.__class__.__name__, field_name)
            ret[field_name].read_only = True

        return ret

    def get_field(self, model_field):
        """
        Creates a default instance of a basic non-relational field.
        """
        kwargs = {}

        if model_field.required:
            kwargs['required'] = False

        if model_field.default:
            kwargs['required'] = False
            kwargs['default'] = model_field.default

        if model_field.__class__ == models.TextField:
            kwargs['widget'] = widgets.Textarea

        # TODO: TypedChoiceField?
#        if model_field.flatchoices:  # This ModelField contains choices
#            kwargs['choices'] = model_field.flatchoices
#            return ChoiceField(**kwargs)

        field_mapping = {
            mongoengine.FloatField: FloatField,
            mongoengine.IntField: IntegerField,
            mongoengine.DateTimeField: DateTimeField,
            mongoengine.EmailField: EmailField,
            mongoengine.URLField: URLField,
            mongoengine.StringField: CharField,
            mongoengine.BooleanField: BooleanField,
            mongoengine.FileField: FileField,
            mongoengine.ImageField: ImageField,
            mongoengine.ObjectIdField: CharField,
            }
        try:
            return field_mapping[model_field.__class__](**kwargs)
        except KeyError:
            return ModelField(model_field=model_field, **kwargs)