# -*- coding: utf-8 -*-
# Many thanks to http://stackoverflow.com/users/400617/davidism
# This code under "I don't care" license
# Take it, use it, learn from it, make it better.
# Start this from cmd or shell or whatever
# Go to favourite browser and type localhost:5000/admin
import sys
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

app = Flask(__name__)

app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite'

# Set echo for debug purposes
app.config['SQLALCHEMY_ECHO'] = True

# Create db instance
db = SQLAlchemy(app)

# Create admin instance 
admin = Admin(app)


class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(200), nullable=False)

    # cover image foreign key
    # use_alter=True along with name='' adds this foreign key after Image has been created to avoid circular dependency
    cover_id = db.Column(db.Integer, db.ForeignKey('image.id', use_alter=True, name='fk_product_cover_id'))

    # cover image one-to-one relationship
    # set post_update=True to avoid circular dependency during
    cover = db.relationship('Image', foreign_keys=cover_id, post_update=True)

class Image(db.Model):
    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id))

    # product gallery many-to-one
    product = db.relationship(Product, foreign_keys=product_id, backref='images')

    # nothing special was need in Image, all circular dependencies were solved in Product

# Need to implement custom Image list
class ProductView(ModelView):
	def __init__(self, session, **kwargs):
   		super(ProductView, self).__init__(Product, session,**kwargs)


class ImageView(ModelView):
	def __init__(self, session, **kwargs):
   		super(ImageView, self).__init__(Image, session,**kwargs)

admin.add_view(ProductView(db.session))
admin.add_view(ImageView(db.session))

if __name__ == '__main__':
        # Create tables
        db.create_all()
        
        # Run in debug mode
        app.debug = True
        
        # Go!
        app.run()

