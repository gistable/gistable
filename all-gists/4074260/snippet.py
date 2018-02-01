from zope.interface import Interface, Attribute, implements
from zope.component import getGlobalSiteManager, adapts


# here is what our data looks like

class IKey(Interface):
    pass

class IEntity(Interface):
    key = Attribute("""The key by which this IEntity can be addressed""")
    value = Attribute("""A bytearray of data accessible by the key""")

# and some concrete implementations of the data interface

class Key(str):
    implements(IKey)

class Entity(object):
    implements(IEntity)

    def __init__(self, key, value):
        self.key = key
        self.value = value

# here are some ways in which the above data can be manipulated

class IDatabase(Interface):
    def put(self, key, value):
        """Write a value to the database accessible later by key"""

    def get(self, key):
        """Retrieve a value from the database"""

class IWriter(Interface):
    def write(self):
        """Write an Entity to the database"""

class IReader(Interface):
    def read(self):
        """Read an entity from the database"""

# and here are some concrete implementations of data manipulation

site = getGlobalSiteManager()
storage = {}

class InMemoryDatabase(object):
    implements(IDatabase)
    def __init__(self):
        self.storage = storage

    def put(self, key, value):
        self.storage[key] = value

    def get(self, key):
        return self.storage[key]


site.registerUtility(InMemoryDatabase, IDatabase, 'db:inMem')

# set our database to db:inMem by default (configuration post to come)
DB_FACTORY = 'db:inMem'

class EntityWriter(object):
    implements(IWriter)
    adapts(IEntity)

    def __init__(self, entity):
        self.entity = entity

    def write(self):
        db = site.getUtility(IDatabase, DB_FACTORY)()
        db.put(self.entity.key, self.entity.value)


class EntityReader(object):
    implements(IReader)
    adapts(IKey)

    def __init__(self, key):
        self.key = key

    def read(self):
        db = site.getUtility(IDatabase, DB_FACTORY)()
        val = db.get(self.key)
        return Entity(self.key, val)

site.registerAdapter(EntityWriter)
site.registerAdapter(EntityReader)

## ACTUAL TESTS!

from zope.component import getAdapter

# write an entity
entity = Entity('thekey', 'thevalue')
getAdapter(entity, IWriter).write()

## read an entity
key = Key('thekey')
entity = getAdapter(key, IReader).read()

print "Entity is:", entity