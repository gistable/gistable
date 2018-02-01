#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy

"""
Flask-SQLAlchemy many-to-many relationship using helper table
http://flask-sqlalchemy.pocoo.org/2.1/models/
Hippies love their dogs.
Dogs love their hippies.
"""
app = Flask(__name__)
db = SQLAlchemy(app)

class Dogs(object):
    """
    Dogs object the "dogs" table.
    """
    def __init__(self, dog_id, hippie_id):
        self.dog_id = dog_id
        self.hippie_id = hippie_id

# "helper" table
dogs = db.Table("dogs",
        db.metadata,
        db.Column("id", db.Integer, primary_key = True),
        db.Column("dog_id", db.Integer, db.ForeignKey("dog.id")),
        db.Column("hippie_id", db.Integer, db.ForeignKey("hippie.id")),
        )
# unique index of hippie_id and dog_id
db.Index("love", dogs.c.hippie_id, dogs.c.dog_id, unique = True)

class Hippie(db.Model):
    """
    Hippie model contains relationship to "Dog"
    secondary table "dogs" is "helper" table which contains
    unique index of Hippie.id and Dog.id
    the backref "hippies" provides a query object for Dog
    """
    __tablename__ = "hippie"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    dogs = db.relationship("Dog",
            secondary=dogs,
            backref=db.backref("hippies", lazy="dynamic"),
            )

class Dog(db.Model):
    """
    Dog table receives backref to "hippies" when a "Hippie" entry is created.
    """
    __tablename__ = "dog"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique=True, nullable=False)

# add in our routes.
@app.route("/hippie/<string:name>")
def hippie(name):
    """
    accept a hippie name
    success: json object({"hippie name": id})
    fail: error
    """
    try:
        hippie = Hippie(name=name)
        db.session.add(hippie)
        db.session.commit()
        return json.dumps({name: hippie.id})
    except Exception as error:
        return(str(error))

@app.route("/dog/<string:name>")
def dog(name):
    """
    accept a dog name
    success: json object({"dog name": id})
    fail: error
    """
    try:
        dog = Dog(name=name)
        db.session.add(dog)
        db.session.commit()
        return json.dumps({name: dog.id})
    except Exception as error:
        return(str(error))

@app.route("/love/<int:hippie_id>/<int:dog_id>")
def love(hippie_id, dog_id):
    """
    Dog love's it's hippie.
    Hippie loves's it's dog.
    create unique relationship in "dogs" table
    return row id on success
    """
    try:
        love = Dogs(dog_id, hippie_id)
        db.session.add(love)
        db.session.commit()
        return str(love.id)
    except Exception as error:
        return(str(error))

@app.route("/")
def index():
    """
    show all our relationships
    """
    try:
        h = {}
        d = {}
        hippies = Hippie.query.all()
        for hippie in hippies:
            if not hippie.name in h:
                h[hippie.name] = []
            for dog in hippie.dogs:
                h[hippie.name].append(dog.name)

        dogs = Dog.query.all()
        for dog in dogs:
            if not dog.name in d:
                d[dog.name] = []
            for hippie in dog.hippies:
                d[dog.name].append(hippie.name)

        return json.dumps([h, d]) 
    except Exception as error:
        return str(error)

if __name__ == "__main__":
    # one must make sure the Dogs class and dogs table are mapped
    db.mapper(Dogs, dogs)
    db.create_all()
    app.run()
