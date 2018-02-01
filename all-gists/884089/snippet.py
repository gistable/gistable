

# CREATE TABLE foos (
#    id INTEGER IDENTITY(1,1) NOT NULL PRIMARY KEY,
# );

# CREATE TABLE foo_data (
#    foo_id INTEGER NOT NULL REFERENCES proposals(id),      
#    [key] VARCHAR(50) NOT NULL,
#    [type] CHAR(1) NOT NULL DEFAULT 's' CHECK(type IN ('s', 'b', 'i', 'f'))
#    value VARCHAR(MAX),

#    PRIMARY KEY(foo_id, [key])
# );

# INSERT INTO foo_data(proposal_id, [key], [type], value) VALUES(2, 'foo', 's', 'abc');
# INSERT INTO foo_data(proposal_id, [key], [type], value) VALUES(2, 'bar', 'i', '1');
# INSERT INTO foo_data(proposal_id, [key], [type], value) VALUES(2, 'baz', 'f', '2.0');
# INSERT INTO foo_data(proposal_id, [key], [type], value) VALUES(2, 'qux', 'b', 'True');

# http://techspot.zzzeek.org/files/2011/decl_enum.py
class FooDataType(DeclEnum):
    BOOLEAN = 'B', 'Boolean'
    FLOAT = 'F', 'Float'
    STRING = 'S', 'String'
    INTEGER = 'I', 'Integer'
    DECIMAL = 'D', 'Decimal'

class FooData(Base):
    TYPE_MAP = {
        bool:  FooDataType.BOOLEAN,
        float: FooDataType.FLOAT,
        str: FooDataType.STRING,
        int: FooDataType.INTEGER,
        Decimal: FooDataType.DECIMAL
    }

    CASTERS = {
        FooDataType.BOOLEAN: lambda x: bool(int(x)),
        FooDataType.FLOAT: float,
        FooDataType.STRING: str,
        FooDataType.INTEGER: int,
        FooDataType.DECIMAL: Decimal
    }

    foo_id = Column(Integer, ForeignKey('foos.id'), nullable=False,
                      primary_key=True)
    key = Column(String(50), nullable=False, primary_key=True)
    type = Column(FooDataType.db_type(), nullable=False)
    value = Column(String)

    @property
    def casted_value(self):
        return self.CASTERS[self.type](self.value)

    @classmethod
    def build(cls, key, value):
        return cls(key=key,
                   value=value,
                   type=cls.TYPE_MAP[type(value)])


class Foo(Base):
  data_map = relation(FooData,
                        collection_class=column_mapped_collection(FooData.key))
  data = association_proxy('data_map', 'casted_value', creator=FooData.build)