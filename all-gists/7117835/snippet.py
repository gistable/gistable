class Persistent(type):
    def __new__(self, name, bases, dct):
        self.tables = dict()
        return super(Persistent, self).__new__(self, name, bases, dct)

    def __init__(self, name, bases, dct):
        table = name.lower() + 's'
        self.tables[self] = table
        super(Persistent, self).__init__(name, bases, dct)


class Model(object, metaclass = Persistent):
    def table_name(self):
        return Persistent.tables[self.__class__]


class User(Model):
    pass


u = User()
print(u.table_name())
