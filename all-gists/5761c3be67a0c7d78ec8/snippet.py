import logging
from rest_framework import serializers


class GeneralModelSerializer(serializers.ModelSerializer):
    """ General model serializer that will serialize a model object. It will return all the model fields.
    """
    class Meta:
        model = None

    def __init__(self, instance):
        self.Meta.model = type(instance)
        super(GeneralModelSerializer, self).__init__(instance=instance)


class FeedSerializer(serializers.ModelSerializer):
    target_object = serializers.SerializerMethodField('get_serialized_target_object')

    SERIALIZERS = {
        'accounts.user': MinimalUserSerializer,
        'posts.post': MinimalPostSerializer
    }

    class Meta:
        model = Action
        fields = ('id', 'target_object', 'timestamp', 'public')

    def get_serialized_target_object(self, obj):
        """ Serialize a model object
         If the object does not have special serializer class use the general one
        """
        content_type, pk = obj.target_content_type, obj.target_object_id
        if content_type and pk:
            model_class = content_type.model_class()
            try:
                instance = model_class.objects.get(pk=pk)
            except model_class.DoesNotExist:
                return None
            app_model = '{0}.{1}'.format(content_type.app_label,content_type.model)
            if app_model in self.SERIALIZERS.keys():
                serializer = self.SERIALIZERS[app_model]
            else:
                logger = logging.getLogger(__name__)
                logger.error('No secure serializer found for {0}'.format(app_model))
                serializer = GeneralModelSerializer
            return serializer(instance=instance).data
        else:
            return None
