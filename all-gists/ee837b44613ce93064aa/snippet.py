import six
from rest_framework import serializers, exceptions, parsers


class PullSerializerMixin(object):
    pull_model = None

    def __init__(self, *args, **kwargs):
        self.pull_model = kwargs.pop('pull_model', self.pull_model)
        super(PullSerializerMixin, self).__init__(*args, **kwargs)

    def get_pull_model(self):
        if not self.pull_model:
            raise NotImplementedError("pull_model not specified")
        return self.pull_model


def pull_fields(pull_spec):
    """
    identify fields required at root of pull spec
    """
    fields = []
    for item in pull_spec:
        if isinstance(item, dict):
            for k in item.iterkeys():
                fields.append(k)
        elif isinstance(item, basestring):
            fields.append(item)
        else:
            raise AssertionError("Expected dicts and strings, got {}".format(item))
    return set(fields)


def pull_field_spec(pull_spec, field_name):
    """
    Looks for recursive field definition in pull spec.

    Match is dict key of field_name, associated value is field pull spec.
    """
    for item in pull_spec:
        if isinstance(item, dict):
            for k, v in item.iteritems():
                if field_name == k:
                    return v


def select_keys(m, ks):
    """
    Destructively select keys on map, uses m.pop(k).
    """
    for k in set(m.keys()) - set(ks):
        m.pop(k)


class PullMixin(object):
    """
    Pull API integration.  Serializer fields will be filtered
    based on the recursive pull spec provided as query param.

    TODO: This seems to cause a conflict with setting metadata_class
    which I'm yet to investigate.
    """

    serializer_pull_field_mapping = {}
    default_pull_parser = parsers.JSONParser
    pull_allowed_methods = ['GET']

    def pull_parser(self):
        for parser in self.request.parsers:
            if parser.media_type == self.request.accepted_media_type:
                return parser
        return self.default_pull_parser

    @property
    def pull_spec(self):
        if not hasattr(self, "_pull"):
            self._pull = None
            if 'pull' in self.request.query_params:
                try:
                    parser_class = self.pull_parser()
                    self._pull = parser_class().parse(
                        six.StringIO(self.request.query_params['pull'])
                    )
                except ValueError as e:
                    pass
        return self._pull

    def get_serializer(self, *args, **kwargs):
        serializer = super(PullMixin, self).get_serializer(*args, **kwargs)
        if self.pull_spec and self.request.method in self.pull_allowed_methods:
            self.recursive_select_keys(serializer, self.pull_spec)
        return serializer

    def get_pull_serializer(self, model, *args, **kwargs):
        """
        Return the serializer instance that should be used for serializing model.
        """
        serializer_class = self.get_pull_serializer_class(model)
        return serializer_class(*args, **kwargs)

    def get_pull_serializer_class(self, model):
        """
        Return the class to use for the model serializer.
        Defaults to using `self.pull_serializer_class`.
        """

        if model in self.serializer_pull_field_mapping:
            return self.serializer_pull_field_mapping[model]

        raise exceptions.PermissionDenied(
            "Model not whitelisted for pull: {}"
                .format(model._meta))

    def recursive_select_keys(self, serializer, pull_spec):
        """
        Destructively and recursively filter serializer fields
        based on pull_spec
        """

        if not pull_spec: return

        if isinstance(serializer, serializers.ListSerializer):
            serializer = serializer.child

        spec_fields = pull_fields(pull_spec)
        if not "*" in spec_fields:
            select_keys(serializer.fields, spec_fields)

        for field_name, field in serializer.fields.iteritems():
            field_spec = pull_field_spec(pull_spec, field_name)

            if field_spec and isinstance(field, serializers.ManyRelatedField):

                child = field.child_relation

                if isinstance(child, PullSerializerMixin):
                    model = child.get_pull_model()
                    field = self.get_pull_serializer(model, read_only=True, many=True)
                    serializer.fields[field_name] = field
                elif child.queryset is None:
                    raise exceptions.NotAcceptable(
                        "Unable to resolve pull serializer on ManyRelatedField which have no queryset. "
                        "Try using the PullSerializerMixin to specify reverse relations. "
                    )
                else:
                    model = child.queryset.model
                    field = self.get_pull_serializer(model, read_only=True, many=True)
                    serializer.fields[field_name] = field

            elif field_spec and isinstance(field, serializers.RelatedField):

                model = field.queryset.model
                field = self.get_pull_serializer(model, read_only=True)
                serializer.fields[field_name] = field

            self.recursive_select_keys(field, field_spec)
