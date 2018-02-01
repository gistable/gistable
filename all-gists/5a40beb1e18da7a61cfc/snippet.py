class WithoutNoneFieldsSerializer(serializers.ModelSerializer):

    """ Exclude model fields which are ``None``.

    This eventually includes foreign keys and other special fields.

    Source: https://gist.github.com/Karmak23/5a40beb1e18da7a61cfc
    """

    def to_native(self, obj):
        """ Remove all ``None`` fields from serialized JSON. 

        .. todo:: the action test is probably superfluous.
        """

        try:
            action = self.context.get('view').action

        except:
            # cf. http://dev.1flow.net/codega-studio/popshake/group/44727/
            # Happens for example when overriding the retreive method, where
            # view/action is missing from the context.
            action = None

        removed_fields = {}

        if action in (None, 'list', 'retrieve', 'create', 'update', ):
            if obj is not None:
                fields = self.fields.copy()

                for field_name, field_value in fields.items():
                    if isinstance(field_value,
                                  serializers.SerializerMethodField):

                        if getattr(self, field_value.method_name)(obj) is None:
                            removed_fields[field_name] = self.fields.pop(field_name)

                    else:
                        try:
                            if getattr(obj, field_name) is None:
                                removed_fields[field_name] = self.fields.pop(field_name)
                        except:
                            LOGGER.exception(u'Could not getattr %s on %s',
                                             field_name, obj)

        # Serialize with the None fields removed.
        result = super(WithoutNoneAttributesSerializer, self).to_native(obj)

        # Restore removed fields in case we are serializing a QS
        # and other instances have the field non-None.
        self.fields.update(removed_fields)

        return result
