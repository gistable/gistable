# Using the `@property` decorator allows the MongoEngine Document object to have
# properties that reference Models, and be got/set like normal foreign keys.
# This same pattern can work the other way and allow Models interface with
# Documents.

class Foo(mongoengine.Document):
    # The `id` of the property is stored in the Document.
    user_id         = mongoengine.IntField()

    # Setters and getters to interface with the SQL DB and set Users to the
    # user property directly.
    @property
    def user(self):
        # Lazily dereference the Model, and cache the object in the `_data`
        # property to avoid repeated fetching.
        if 'user' not in self._data:
            self._data['user'] = User.objects.get(pk=self.user_id)
        return self._data['user']
    
    @user.setter
    def user(self, value):
        # Cache the value in the `_data` attribute and set the corresponding
        # `id` property.
        if value and hasattr(value, 'pk'):
            self._data['user'] = value
            self.user_id = value.pk
        else:
            self._data['user'] = None
            self.user_id = None
    
    @user.deleter
    def user(self):
        self._data['user'] = None
        self.user_id = None
