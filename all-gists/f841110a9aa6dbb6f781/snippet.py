class PrimaryKeyInObjectOutRelatedField(relations.PrimaryKeyRelatedField):
    """
    Django Rest Framework RelatedField which takes the primary key as input to allow setting relations,
    but takes an optional `output_serializer_class` parameter, which if specified, will be used to
    serialize the data in responses.
    
    Usage:
        class MyModelSerializer(serializers.ModelSerializer):
            related_model = PrimaryKeyInObjectOutRelatedField(
                queryset=MyOtherModel.objects.all(), output_serializer_class=MyOtherModelSerializer)
    
            class Meta:
                model = MyModel
                fields = ('related_model', 'id', 'foo', 'bar')
        
    """

    def __init__(self, **kwargs):
        self._output_serializer_class = kwargs.pop('output_serializer_class', None)
        super(PrimaryKeyInObjectOutRelatedField, self).__init__(**kwargs)

    def use_pk_only_optimization(self):
        return not bool(self._output_serializer_class)

    def to_representation(self, obj):
        if self._output_serializer_class:
            data = self._output_serializer_class(obj).data
        else:
            data = super(PrimaryKeyInObjectOutRelatedField, self).to_representation(obj)
        return data
