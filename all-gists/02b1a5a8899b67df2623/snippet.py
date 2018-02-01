from sqlalchemy import func
from sqlalchemy.types import UserDefinedType, Float


class EasyGeometry(UserDefinedType):

    def get_col_spec(self):
        return "GEOMETRY"

    def bind_expression(self, bindvalue):
        return func.ST_GeomFromText(bindvalue, type_=self)

    def column_expression(self, col):
        return func.ST_AsText(col, type_=self)

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            assert isinstance(value, tuple)
            lat, lng = value
            return "POINT(%s %s)" % (lng, lat)
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            #m = re.match(r'^POINT\((\S+) (\S+)\)$', value)
            #lng, lat = m.groups()
            lng, lat = value[6:-1].split()  # 'POINT(135.00 35.00)' => ('135.00', '35.00')
            return (float(lat), float(lng))
        return process


## example
if __name__ == '__main__':
 
    class Example(Base):
        __tablename__ = 'example'
        id    = Column(Integer, primary_key=True)
        geo   = Column(EasyGeometry)
    
    lat, lng = 35.658704, 139.745408
    ex1 = Example(id=1, geo=(lat, lng))
    db = DBSession()
    db.add(ex1)
    db.commit()
    
    ex1 = db.query(Example).first()
    print(ex1.geo)   #=> (35.658704, 139.745408)


