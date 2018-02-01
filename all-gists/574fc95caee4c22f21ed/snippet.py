from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    books = db.relationship('Book', backref='author')

    def __repr__(self):
        return '<Author:{}>'.format(self.name)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    def __repr__(self):
        return '<Book:{}>'.format(self.title)


categories = db.Table('categories',
                      db.Column('category_id', db.Integer, db.ForeignKey('category.id')),
                      db.Column('book_id', db.Integer, db.ForeignKey('book.id'))
)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    books = db.relationship('Book', secondary=categories,
                            backref=db.backref('categories', lazy='dynamic'))

    def __repr__(self):
        return '<Category:{}>'.format(self.name)


with app.app_context():
    db.create_all()

    bob = Author(name='Bob')
    dune = Book(title='Dune')
    moby_dick = Book(title='Moby Dick')

    carol = Author(name='Carol')
    ring_world = Book(title='Ring World')
    fahrenheit = Book(title='Fahrenheit 451')

    bob.books = [dune, moby_dick]
    carol.books = [ring_world, fahrenheit]

    db.session.add(bob)
    db.session.add(carol)
    db.session.commit()

    author = Author.query.filter_by(name='Bob').first()
    print author  # <Author:Carol>
    print author.books  # [<Book:Ring World>, <Book:Fahrenheit 451>]

    dune_book = Book.query.filter_by(title='Dune').first()
    print dune_book  # <Book:Dune>
    print dune_book.author  # <Author:Bob>

    scifi = Category(name='Science Fiction')
    classic = Category(name='Classic')

    classic.books = [moby_dick, dune, fahrenheit]
    scifi.books = [dune, ring_world]

    db.session.add_all([classic, scifi])
    db.session.commit()

    print dune, dune.categories.all()
    print dune.categories.filter(Category.name.ilike('sci%')).all()

    alice = Author(name='Alice')
    beowulf = Book(title='Beowulf')
    beowulf.author = alice
    beowulf.categories = [classic]
    db.session.add(beowulf)
    db.session.commit()

    print Author.query.join(Author.books).filter(
        Book.categories.contains(scifi)).all()

    print Category.query.join(Category.books).filter(
        Book.author==carol).all()
