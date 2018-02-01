from rest_framework import serializers

class ListSerializer(serializers.Serializer):
    def from_native(self, data):
        if isinstance(data, list):
            return list(data)
        else:
            msg = self.error_messages['invalid']
            raise serializers.ValidationError(msg)

    def to_native(self, obj):
        return obj