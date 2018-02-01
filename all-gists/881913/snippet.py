SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

class BaseModel(db.Model):

    def to_json_friendly_value(self, v):
        if v is None or isinstance(v, SIMPLE_TYPES):
            value = v
        elif isinstance(v, datetime.date):
            # Convert date/datetime to ms-since-epoch ("new Date()").
            ms = time.mktime(v.utctimetuple()) * 1000
            ms += getattr(v, 'microseconds', 0) / 1000
            value = int(ms)
        elif isinstance(v, db.Model):
            value = v.key()
        else:
            raise ValueError('cannot encode ' + repr(prop))
        return value
    
    def to_dict(self, props=None, stub=False, indent=None):
        data = {"id": self.key().id()}
        for key, prop in self.properties().iteritems():
            if props and key not in props:
                continue
            if type(prop) is db.ReferenceProperty:
                ref = prop.get_value_for_datastore(self)
                if ref:
                    data["%s_id" % key] = self.to_json_friendly_value( ref.id() )
            else:
                data[key] = self.to_json_friendly_value( getattr(self, key) )
        # add the stub value if we have truncated the props
        if stub and len(self.__class__.optional_properties) > 0:
            data["stub"] = True            
        
    def to_json(self, props=None, stub=False, indent=None):
        return simplejson.dumps( self.to_dict, indent=indent )
    	
