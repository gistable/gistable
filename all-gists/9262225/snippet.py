import psycopg2.extras
import sqlalchemy.dialects.postgresql
from sqlalchemy.types import TypeEngine
from sqlalchemy.types import String
from sqlalchemy.types import TypeDecorator
import uuid

# Required for PostgreSQL to accept UUID type.
psycopg2.extras.register_uuid()

class UUID(TypeDecorator):
    """ Converts UUID to string before storing to database.
        Converts string to UUID when retrieving from database. """

    impl = TypeEngine

    def load_dialect_impl(self, dialect):
        """ When using Postgres database, use the Postgres UUID column type.
            Otherwise, use String column type. """
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(sqlalchemy.dialects.postgresql.UUID)

        return dialect.type_descriptor(String)

    def process_bind_param(self, value, dialect):
        """ When using Postgres database, no conversion.
            Otherwise, convert to string before storing to database. """
        if dialect.name == 'postgres':
            return value

        if value is None:
            return value

        return str(value)

    def process_result_value(self, value, dialect):
        """ When using Postgres database, no conversion.
            Otherwise, convert to UUID when retrieving from database. """
        if dialect.name == 'postgresql':
            return value

        if value is None:
            return value

        return uuid.UUID(value)
