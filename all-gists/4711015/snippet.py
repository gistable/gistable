
# This is a very crud example of using the Repository Pattern with SQLAlchemy. It allows me to completely ignore interactions with 
# the database. This is only pulled in whenever I require to persist or retrieve an object from the database. The domain/business 
# logic is entirely separated from persistence and I can have true unit tests for those.

# The tests for persistence are then limited to very specific cases of persistence and retrieving instances, and I can do those 
# independent of the business logic. They also tend to be less tests since I only need to test them once.



class Person(object):   
    def __init__(self):
        # This is entity is mapped to the DB using SQLAlchemy's classical mapping.
        It also includes an Address
        pass

class Address(object):
    def __init__(self):
        pass

class PersonRepository(object):
     def __init__(self, DBSession):
         self.session = DBSession

     def persist(self, entity):
         self.session.add(entity)
         self.session.flush()
         return entity


class AddressEditor(object):
    def __init__(self):
        pass

    def add_address(self, person, address):
        person.address = address
        #We can either inject the session into this method, or 
        #obtain it from a configuration file.
        repository = PersonRepository(DBSession)
        person = repository.persist(person)
        return person.address




