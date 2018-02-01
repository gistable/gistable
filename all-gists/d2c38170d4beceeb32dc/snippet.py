from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask.ext.principal import Permission, RoleNeed


# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'

# MongoDB Config
app.config["MONGODB_HOST"] = "mongodb://localhost:27017/flask_security"
app.config["MONGODB_DB"] = True

# Create database connection object
db = MongoEngine(app)

# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('admin'))


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])


# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create a user to test with
@app.before_first_request
def create_user():
    test_role = user_datastore.find_or_create_role('test')
    user_datastore.create_user(
        email='a@example.com', password='abc123', roles=[test_role]
    )
    admin_role = user_datastore.find_or_create_role('admin')
    user_datastore.create_user(
        email='b@example.com', password='abcd1234',
        roles=[admin_role]
    )


# Views
@app.route('/')
@login_required
def home():
    return 'private'


@app.route('/protected')
@login_required
@admin_permission.require()
def protected():
    return 'protected'


if __name__ == '__main__':
    app.run()
