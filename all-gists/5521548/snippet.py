from flask import Flask, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.admin.contrib import sqlamodel
from flask.ext import admin

# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


# Create models
class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __unicode__(self):
        return self.name


class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))

    parent_id = db.Column(db.Integer(), db.ForeignKey(Parent.id), nullable=False)
    parent = db.relationship(Parent, backref='children')

    def __unicode__(self):
        return self.name


# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


# Customized Post model admin
class ChildAdmin(sqlamodel.ModelView):
    # Hook form creation methods
    def create_form(self):
        return self._use_filtered_parent(super(ChildAdmin, self).create_form())

    def edit_form(self, obj):
        return self._use_filtered_parent(super(ChildAdmin, self).edit_form(obj))

    # Logic
    def _use_filtered_parent(self, form):
        form.parent.query_factory = self._get_parent_list
        return form

    def _get_parent_list(self):
        return self.session.query(Parent).filter_by(name='test').all()


if __name__ == '__main__':
    # Create admin
    a = admin.Admin(app, 'Simple Models')

    # Add views
    a.add_view(sqlamodel.ModelView(Parent, db.session))
    a.add_view(ChildAdmin(Child, db.session))

    # Create DB
    db.create_all()

    # Start app
    app.debug = True
    app.run('0.0.0.0', 8000)
