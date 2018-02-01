import sqlalchemy as sa

class EnumIntType(sa.types.TypeDecorator):
    impl = sa.types.SmallInteger

    values = None

    def __init__(self, values=None):
        sa.types.TypeDecorator.__init__(self)
        self.values = values

    def process_bind_param(self, value, dialect):
        return None if value == None else self.values.index(value)

    def process_result_value(self, value, dialect):
        return None if value == None else self.values[value]