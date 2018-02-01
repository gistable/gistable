# Based on http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/

import six
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import SchemaType, TypeDecorator, Enum
from sqlalchemy import __version__, text, cast
import re

if __version__ < '0.6.5':
    raise NotImplementedError("Version 0.6.5 or higher of SQLAlchemy is required.")

class EnumSymbol(object):
    """Define a fixed symbol tied to a parent class."""

    def __init__(self, cls_, name, value, description):
        self.cls_ = cls_
        self.name = name
        self.value = value
        self.description = description

    def __reduce__(self):
        """Allow unpickling to return the symbol
        linked to the DeclEnum class."""
        return getattr, (self.cls_, self.name)

    def __iter__(self):
        return iter([self.value, self.description])

    def __repr__(self):
        return "<%s>" % self.name

class EnumMeta(type):
    """Generate new DeclEnum classes."""

    def __init__(cls, classname, bases, dict_):
        cls._reg = reg = cls._reg.copy()
        for k, v in dict_.items():
            if isinstance(v, tuple):
                sym = reg[v[0]] = EnumSymbol(cls, k, *v)
                setattr(cls, k, sym)
        return type.__init__(cls, classname, bases, dict_)

    def __iter__(cls):
        return iter(cls._reg.values())

class DeclEnum(six.with_metaclass(EnumMeta)):
    """Declarative enumeration."""

    _reg = {}

    @classmethod
    def from_string(cls, value):
        try:
            return cls._reg[value]
        except KeyError:
            raise ValueError(
                    "Invalid value for %r: %r" %
                    (cls.__name__, value)
                )

    @classmethod
    def values(cls):
        return cls._reg.keys()

    @classmethod
    def db_type(cls, **kwargs):
        return DeclEnumType(cls, **kwargs)

class DeclEnumType(SchemaType, TypeDecorator):
    def __init__(self, enum, **kwargs):
        self.enum = enum
        self.impl = Enum(
                        *enum.values(),
                        name="ck%s" % re.sub(
                                    '([A-Z])',
                                    lambda m:"_" + m.group(1).lower(),
                                    enum.__name__),
                        **kwargs
                    )
        super(DeclEnumType, self).__init__(**kwargs)

    def _set_table(self, table, column):
        self.impl._set_table(table, column)

    def copy(self):
        return DeclEnumType(self.enum)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum.from_string(value.strip())

    def register_with_psycopg(self, conn):
        import psycopg2.extensions
        my_enum_array_oid = conn.execute(text(
            "SELECT typarray FROM pg_catalog.pg_type "
            "WHERE typname = :tn"
        ), tn=self.impl.name).scalar()
        psycopg2.extensions.register_type(
            psycopg2.extensions.new_array_type(
                (my_enum_array_oid,),
                self.impl.name + '[]',
                psycopg2.STRING)
        )

if __name__ == '__main__':
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, String, create_engine
    from sqlalchemy.orm import Session

    Base = declarative_base()

    class EmployeeType(DeclEnum):
        part_time = "P", "Part Time"
        full_time = "F", "Full Time"
        contractor = "C", "Contractor"

    class SkillType(DeclEnum):
        intelligence = "I", "Intelligence"
        strength = "S", "Strength"
        agility = "A", "Agility"

    skill_type = SkillType.db_type(metadata=Base.metadata)

    class Employee(Base):
        __tablename__ = 'employee'

        id = Column(Integer, primary_key=True)
        name = Column(String(60), nullable=False)
        type = Column(EmployeeType.db_type())
        skills = Column(postgresql.ARRAY(skill_type))

        def __repr__(self):
             return "Employee(%r, %r, %r)" % (self.name, self.type, self.skills)

    e = create_engine('postgresql://postgres:password@/test_arrays', echo=True)
    Base.metadata.create_all(e)
    skill_type.register_with_psycopg(e)

    sess = Session(e)

    sess.add_all([
        Employee(name='e1', type=EmployeeType.full_time),
        Employee(name='e2', type=EmployeeType.full_time,
                 skills=cast([SkillType.agility, SkillType.intelligence], postgresql.ARRAY(skill_type))),
        Employee(name='e3', type=EmployeeType.part_time,
                 skills=cast([SkillType.intelligence], postgresql.ARRAY(skill_type))),
        Employee(name='e4', type=EmployeeType.contractor, skills=[]),
        Employee(name='e5', type=EmployeeType.contractor,
                 skills=cast([SkillType.strength, SkillType.agility], postgresql.ARRAY(skill_type))),
    ])
    sess.commit()

    print(sess.query(Employee).filter_by(type=EmployeeType.contractor).all())