'''
This code is an example of Flask-SuperAdmin app with basic authentication. Use it for anything you like.

Based on this snippet: http://flask.pocoo.org/snippets/8/
'''
import flask
from flask.ext.superadmin import Admin, expose, AdminIndexView as _AdminIndexView
from flask.ext.superadmin.model import ModelAdmin as _ModelAdmin
from flask.ext.sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)


def check_auth(username, password):
    return username == password == 'admin'

def authenticate():
    return flask.Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def is_authenticated():
    auth = flask.request.authorization
    return auth and check_auth(auth.username, auth.password)


class ModelAdmin(_ModelAdmin):

    def is_accessible(self):
        return is_authenticated()

    def _handle_view(self, name, *args, **kwargs):
        if not self.is_accessible():
            return authenticate()


class AdminIndexView(_AdminIndexView):
    @expose('/')
    def index(self):
        if not is_authenticated():
            return authenticate()
        return super(AdminIndexView, self).index()


admin = Admin(app, index_view=AdminIndexView())
admin.register(User, admin_class=ModelAdmin, session=db.session)

if __name__ == '__main__':
    app.run()
