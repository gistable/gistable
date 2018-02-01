# -*- coding: utf-8 -*-
from __future__ import absolute_import

from enum import Enum
from sqlalchemy.types import SchemaType, TypeDecorator
from sqlalchemy.types import Enum as SAEnum


class EnumType(SchemaType, TypeDecorator):
    def __init__(self, enum, name):
        self.enum = enum
        self.name = name
        members = (member.value for member in enum)
        kwargs = {'name': name}

        self.impl = SAEnum(*members, **kwargs)

    def _set_table(self, table, column):
        self.impl._set_table(table, column)

    def copy(self):
        return EnumType(self.enum, self.name)

    def process_bind_param(self, enum_instance, dialect):
        if enum_instance is None:
            return None

        return enum_instance.value

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return self.enum(value)


class DBEnum(Enum):
    def __init__(self, db_repr, description=None):
        if description is None:
            description = db_repr
            db_repr = self.name

        self._value_ = db_repr
        self.description = description

    @classmethod
    def as_type(cls, name):
        return EnumType(cls, name)

    @classmethod
    def get_description_mapping(cls):
        return dict((member.name, member.description) for member in cls)


# EXAMPLE USAGE
class ClientType(DBEnum):
    private = 'Private'  # Database representation will be equal to enum name => 'private'
    company = 'co', 'Company'  # Database representation will be overriden, and will become => 'co'


class Client(declarative_base()):
    type = sa.Column(ClientType.as_type('ck_client_type'), nullable=False)
