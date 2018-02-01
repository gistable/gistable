class ResponseDataObject(object):

    def __init__(self, mydict={}):
        self._load_dict(mydict)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return str(self.__dict__)

    def _load_dict(self, mydict):
        
        for a in mydict.items():

            if isinstance(a[1], dict):
                o = ResponseDataObject(a[1])
                setattr(self, a[0], o)

            elif isinstance(a[1], list):
                objs = []
                for i in a[1]:
                    objs.append(ResponseDataObject(i))
                
                setattr(self, a[0], objs)
            else:
                setattr(self, a[0], a[1])