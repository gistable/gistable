class Container(dict):
    def __init__(self, *args, **kwargs):
        super(Container, self).__init__(*args, **kwargs)
        self._shared = set()
        self._instances = {}
        
    def __getitem__(self, key):
        if key in self._instances:
            return self._instances[key]
            
        value = super(Container, self).__getitem__(key)
        value = value(self) if callable(value) else value
        
        if key in self._shared:
            self._instances[key] = value
        
        return value
    
    def share(self, key):
        self._shared.add(key)

class Database(object):
    def __init__(self, *args):
        pass

container = Container()

container['db_user'] = 'root'
container['db_pass'] = '123'
container['db_host'] = 'localhost'
container['db'] = lambda c: Database(c['db_user'], c['db_pass'], c['db_host'])
container.share('db')

database = container['db']