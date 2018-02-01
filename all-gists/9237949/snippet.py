class RestrictedSerializerOptions(serializers.ModelSerializerOptions):
    """
    Meta class options for ModelSerializer
    """
    def __init__(self, meta):
        super(RestrictedSerializerOptions, self).__init__(meta)
        self.writable_fields = getattr(meta, 'writable_fields', ())


class WriteRestrictedModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `writable_fields` argument that
    controls which fields can be written to.
    """
    _options_class = RestrictedSerializerOptions

    def __init__(self, *args, **kwargs):
        super(WriteRestrictedModelSerializer, self).__init__(*args, **kwargs)

        # Any fields not writable are set to read_only.
        writable = set(self.opts.writable_fields)
        existing = set(self.fields.keys())
        for field_name in existing - writable:
            self.fields[field_name].read_only = True


"""
Use will look something like:

class TourSerializer(WriteRestrictedModelSerializer):
    building = BuildingSerializer()

    class Meta:
        model = Tour
        writable_fields = ('time',)
"""