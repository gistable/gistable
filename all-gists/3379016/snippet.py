import unittest
from mongoengine import *


class Test(unittest.TestCase):

    def setUp(self):
        conn = connect(db='mongoenginetest')

    def create_old_data(self):
        class Person(Document):
            name = StringField()
            age = FloatField()  # Save as string

            meta = {'allow_inheritance': True}

        Person.drop_collection()

        Person(name="Rozza", age=35.00).save()

        rozza = Person._get_collection().find_one()
        self.assertEqual(35.00, rozza['age'])

    def test_migration(self):

        self.create_old_data()

        class Person(Document):
            name = StringField()
            age = StringField()

            meta = {'allow_inheritance': True}

        for p in Person.objects:
            p.age = "%s" % p.age
            p.save()

        rozza = Person.objects.first()
        self.assertEqual("35.0", rozza.age)

if __name__ == '__main__':
    unittest.main()
