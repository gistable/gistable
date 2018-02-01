import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
import uuid
 
engine = sqlalchemy.create_engine('sqlite:///:memory:')
Base = declarative_base()
 
 
class Order_Product(Base):
  __tablename__ = 'order_product'
  id = Column(String(35), primary_key=True, unique=True)
  order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
  product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
  quantity = Column(Integer)

  order = relationship("Order", backref=backref("order_products", cascade="all, delete-orphan" ))
  product = relationship("Product", backref=backref("order_products", cascade="all, delete-orphan" ))

  def __init__(self, order=None, product=None, quantity=None):
    self.id = uuid.uuid4().hex
    self.order = order
    self.product =  product
    self.quantity = quantity

  def __repr__(self):
    return '<Order_Product {}>'.format(self.order.name+" "+self.product.name)


 
 
class Product(Base):
  __tablename__ = 'products'
  id = Column(String(35),  primary_key=True, unique=True)
  name = Column(String(80), nullable=False)
  
  orders = relationship("Order", secondary="order_product", viewonly=True)
 
  def __init__(self, name):
    self.id = uuid.uuid4().hex
    self.name = name
    self.orders=[]
   
  def __repr__(self):
    return '<Product {}>'.format(self.name)
 
 
class Order(Base):
  __tablename__ = 'orders'
  id = Column(String(35),  primary_key=True, unique=True)
  name = Column(String(80), nullable=False)

  products = relationship("Product", secondary="order_product", viewonly=True)

  def add_products(self, items):
    for product, qty in items:
      self.order_products.append(Order_Product(order=self, product=product, quantity=qty))
      
  

 
  def __init__(self, name):
    self.id = uuid.uuid4().hex
    self.name = name
    self.products =[]
   
  def __repr__(self):
    return '<Order {}>'.format(self.name)
 
 
Base.metadata.create_all(engine)
 
Session = sessionmaker(bind=engine)
session = Session()
 
prod1 = Product(name="Oreo")
prod2 = Product(name="Hide and Seek")
prod3 = Product(name="Marie")
prod4 = Product(name="Good Day")


session.add_all([prod1, prod2, prod3, prod4])
session.commit()

order1 = Order( name = "First Order")
order2 = Order( name = "Second Order")


order1.add_products([ (prod1,4) , (prod2,5) , (prod3,4) ])
order2.add_products([ (prod2,6) , (prod1,1) , (prod3,2), (prod4,1) ])

session.commit()


print "Products array of order1: "
print order1.products
print "Products array of order2: "
print order2.products
print "Orders array of prod1: "
print prod1.orders
print "Orders array of prod2: "
print prod2.orders
print "Orders array of prod3: "
print prod3.orders
print "Orders array of prod4: "
print prod4.orders

print "Order_Products Array of order1 : "
print order1.order_products

print "Order_Products Array of prod1 : "
print prod1.order_products