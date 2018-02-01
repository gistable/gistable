def nested_from_native(nested_field, data):
  if isinstance(nested_field, serializers.BaseSerializer):
    return nested_field.from_native(data, None)
  return nested_field.from_native(data)


class ListField(fields.WritableField):

  def __init__(self, item_field, *args, **kwargs):
    super(ListField, self).__init__(*args, **kwargs)
    self.item_field = item_field

  def to_native(self, obj):
    if obj:
      return [
        self.item_field.to_native(item)
        for item in obj
      ]

  def from_native(self, data):
    if data:
      return [
        nested_from_native(self.item_field, item_data)
        for item_data in data
      ]
