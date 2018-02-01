from peewee import *

class BModel(Model):
    class Meta:
        database = db

    @classmethod
    def create_table(cls, *args, **kwargs):
        for field in cls._meta.get_fields():
            if hasattr(field, "pre_field_create"):
                field.pre_field_create(cls)

        cls._meta.database.create_table(cls)

        for field in cls._meta.get_fields():
            if hasattr(field, "post_field_create"):
                field.post_field_create(cls)

class EnumField(Field):
    db_field = "enum"

    def pre_field_create(self, model):
        field = "e_%s" % self.name

        self.get_database().get_conn().cursor().execute(
            "DROP TYPE IF EXISTS %s;" % field
        )

        query = self.get_database().get_conn().cursor()

        tail = ', '.join(["'%s'"] * len(self.choices)) % tuple(self.choices)
        q = "CREATE TYPE %s AS ENUM (%s);" % (field, tail)
        query.execute(q)

    def post_field_create(self, model):
        self.db_field = "e_%s" % self.name

    def coerce(self, value):
        if value not in self.choices:
            raise Exception("Invalid Enum Value `%s`", value)
        return str(value)

    def get_column_type(self):
        return "enum"

    def __ddl_column__(self, ctype):
        return SQL("e_%s" % self.name)

class Example(BModel):
    enum = EnumField(choices=["a", "b", "c"])
    
Example.create(enum="a")
Example.get(id=1).enum # "a"
