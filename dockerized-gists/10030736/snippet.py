import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship


engine = sqlalchemy.create_engine('sqlite:///:memory:')
Base = declarative_base()


class Order_Product(Base):
    __tablename__ = 'order_product'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    quantity = Column(Integer)


class Product(Base):
    """ SQLAlchemy Product Model """
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    stock = relationship('Order_Product', backref='product',
                         primaryjoin=id == Order_Product.product_id)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Product {}>'.format(self.name)


class Category(Base):
    """ SQLAlchemy Category Model """
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    stock = relationship('Order_Product', backref='category',
                         primaryjoin=id == Order_Product.category_id)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category {}>'.format(self.name)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

prod = Product(name="Oreo")
prod1 = Product(name="Hide and Seek")

cate1 = Category(name="biscuit")
cate2 = Category(name="creamy")
cate3 = Category(name="chocolate")

op1 = Order_Product(id=1, category_id=cate1.id, product_id=prod.id, quantity=20)
prod.stock.append(op1)
cate1.stock.append(op1)

op2 = Order_Product(id=2, category_id=cate3.id, product_id=prod.id, quantity=10)
prod.stock.append(op2)
cate3.stock.append(op2)

op3 = Order_Product(id=3, category_id=cate1.id, product_id=prod1.id, quantity=40)
prod1.stock.append(op3)
cate1.stock.append(op3)

session.add_all([prod, prod1, cate1, cate2, cate3])
session.commit()

# Get all categories a product belongs to
for p in session.query(Product).all():
    print p.name
    for a in p.stock:
        print session.query(Category).filter_by(id=a.category_id).all()

# Get all products that belong to a cateogory
for c in session.query(Category).all():
    print c.name
    for a in c.stock:
        print session.query(Product).filter_by(id=a.product_id).all()
