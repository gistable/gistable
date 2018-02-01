from google.appengine.ext import ndb

class DynamicPropertyMixin(object):
    """ Facilitates creating dynamic properties on ndb.Expando entities.
        Also works on ndb.Model derived classes!

        Note: keyword args are passed on to the underlying ndb.XxxProperty() class
    """

    def is_prop(self, name):
        return name in self._properties

    def set_dynamic_prop(self, cls, name, value, **kwds):
        """ Creates a typed dynamic property.  This can be particularly useful for
            ndb.PickleProperty and ndb.JsonProperty types in order to take advantage
            of the datastore in/out conversions.

            Note: keyword args are passed on to the underlying ndb.XxxProperty() class
        """
        prop = cls(name, **kwds)
        prop._code_name = name
        self._properties[name] = prop
        prop._set_value(self, value)

    def set_unindexed_prop(self, name, value, **kwds):
        """ Creates a generic unindexed property which is required for Expando to store
            any ndb.BlobProperty() or derived class such as:
                ndb.TextProperty()
                ndb.PickleProperty()
                ndb.JsonProperty()
        """
        self.set_dynamic_prop(ndb.GenericProperty, name, value, indexed=False, **kwds)

    #--- The blob properties ---

    def set_blob_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.BlobProperty, name, value, **kwds)

    def set_text_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.TextProperty, name, value, **kwds)

    def set_pickle_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.PickleProperty, name, value, **kwds)

    def set_json_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.JsonProperty, name, value, **kwds)

    #--- Useful non-blob properties ---

    def set_string_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.StringProperty, name, value, **kwds)

    def set_integer_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.IntegerProperty, name, value, **kwds)

    def set_float_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.FloatProperty, name, value, **kwds)

    def set_datetime_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.DateTimeProperty, name, value, **kwds)

    def set_key_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.KeyProperty, name, value, **kwds)

    #--- Less useful non-blob properties ---

    def set_generic_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.GenericProperty, name, value, **kwds)

    def set_boolean_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.BooleanProperty, name, value, **kwds)

    def set_date_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.DateProperty, name, value, **kwds)

    def set_time_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.TimeProperty, name, value, **kwds)

    def set_user_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.UserProperty, name, value, **kwds)

    def set_geopt_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.GeoPtProperty, name, value, **kwds)

    def set_blobkey_prop(self, name, value, **kwds):
        self.set_dynamic_prop(ndb.BlobKeyProperty, name, value, **kwds)
