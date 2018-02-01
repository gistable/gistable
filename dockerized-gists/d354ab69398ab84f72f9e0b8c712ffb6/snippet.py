# THIS PROJECT IS AN EXAMPLE APP. SOME CODE MAY NOT BE ACTUALLY USEFUL
# FOR DEMONSTRATION PURPOSES ONLY
# YOUR MILEAGE MAY VARY
# Requirements are Flask, Flask-WTF, Flask-SQLAlchemy, bcrypt

import os

from flask import (Flask,
                   Blueprint,
                   redirect,
                   render_template_string,
                   request,
                   url_for)
from flask_login import UserMixin
from flask_principal import Permission, RoleNeed

from flask_security import (
    login_required,
    RoleMixin,
    Security,
    SQLAlchemyUserDatastore,
    utils,
    )
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import (
    HiddenField,
    StringField,
    SubmitField,
    TextAreaField)
from wtforms.validators import DataRequired

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# Instantiate the extensions but do not initialize them yet.
db = SQLAlchemy()
security = Security()

# The following are template strings which are utilized by jinja2. Jinja2
# is a template language which provides specific tags that allow the ability to
# execute python code during the parsing process.

# The index template string for the main page
index_template = '''
<div class="nav">
  {% if current_user.is_authenticated %}
    Welcome, {{ current_user.email }}
    <a href="{{ url_for('security.logout') }}">Logout</a>
    <a href="{{ url_for('blog.blog_index') }}">View All</a>
  {% else %}
  <a href="{{ url_for('security.login') }}">Login</a>
  {% endif %}
</div>

{% if posts %}
  {% for post in posts %}
  <div>
    <h1>{{ post.title }}</h1>
    <p> {{ post.text }} </p>
  {% endfor %}
  </div>
  {% else %}
  <p>No posts yet. Try again later</p>
{% endif %}
'''

blog_index_template = '''
{% if posts %}
    <table class="posts-table">
        <thead>
            <tr>
                <th>post id</th>
                <th>title</th>
                <th>text</th>
            </tr>
        </thead>
        <tbody>
        {% for post in posts %}
            <tr>
                <td>{{ post.id }}</td>
                <td><a href="{{ url_for('blog.edit_post', post_id=post.id) }}">{{ post.title }}</a></td>
                <td>{{ post.text }}</td>
            </tr>
        {% endfor %}
        </tbody>
    </table>
{% else %}
<p> You don't have any posts </p>
{% endif %}
<a href = "{{ url_for('blog.create_post') }}">Create Post</a>
'''

# The template string for creating/editing a blog post
create_post_template = '''
<div class="post-form">
    <form action="{% if form.id %} {{url_for('blog.edit_post', post_id=form.id.data) }} {% else %} {{ url_for('blog.create_post') }} {% endif %}" method="POST" name="post_form">
        {% if form.id %}
            {{ form.id }}
        {% endif %}
        {{ form.csrf_token }}
        {{ form.title.label }}
        {{ form.title }}
        {{ form.text.label }}
        {{ form.text }}
        {{ form.submit() }}
    </form>
</div>
'''

# Customize your own error pages
error_template = '''
<div id="error">
    <h1> Sorry, there was an error</h1>
    <p>Error:# {{ status_code }}</p>
</div>
'''


# Blog post creation form
class CreatePostForm(FlaskForm):
    """
    The form used to create a blog post
    """
    title = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditPostForm(CreatePostForm):
    id = HiddenField()


# Create the Models
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.Text())

    @classmethod
    def all(cls):
        """
        Returns all researcher items from the database
        """
        return db.session.query(cls).all()


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))


class Role(RoleMixin, db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __eq__(self, other):
        return (self.name == other or
                self.name == getattr(other, 'name', None))

    def __ne__(self, other):
        return (self.name != other and
                self.name != getattr(other, 'name', None))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(120))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)
    registered_at = db.Column(db.DateTime())

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


# Create settings object
settings = {
    'SECRET_KEY': 'super not secure development key',
    'DEBUG': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + os.path.join(BASE_PATH,
                                                           'posts.db'),
    'SQLALCHEMY_ECHO': True,
    'SECURITY_PASSWORD_HASH': 'bcrypt',
    'SECURITY_PASSWORD_SALT': os.environ.get('SECURITY_SALT', 'dev secret'),
    'SECURITY_CONFIRMABLE': False,
    'SECURITY_REGISTERABLE': False,
    'SECURITY_TRACKABLE': True,
    'SECURITY_CHANGEABLE': True
}

# Create the main Flask application
app = Flask(__name__)
app.config.update(settings)

# Initialize extensions
db.init_app(app)
security.init_app(app,
                  SQLAlchemyUserDatastore(db, User, Role),
                  register_blueprint=True)


# Public Endpoints
@app.route('/', methods=['GET'])
def index():
    posts = Post.all()
    return render_template_string(index_template, posts=posts)


# Register errorhandlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template_string(error_template, status_code=404), 404


@app.errorhandler(500)
def server_error(e):
    return render_template_string(error_template, status_code=500), 500


# Create blog blueprint
blog = Blueprint('blog', __name__, url_prefix='/blog')

# Create admin role for blog endpoints
admin_permission = Permission(RoleNeed('admin'))


# Create the blog routes
@blog.route('/', methods=['GET'])
@login_required
@admin_permission.require()
def blog_index():
    posts = Post.all()
    return render_template_string(blog_index_template, posts=posts)


@blog.route('/create', methods=['GET', 'POST'])
@login_required
@admin_permission.require()
def create_post():
    form = CreatePostForm(request.form)
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    text=form.text.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('blog.blog_index'))
    return render_template_string(create_post_template, form=form)


@blog.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
@admin_permission.require()
def edit_post(post_id):
    post = Post.query.get(post_id)
    form = EditPostForm(request.form, obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.merge(post)
        db.session.commit()
        return redirect(url_for('blog.blog_index'))
    return render_template_string(create_post_template, form=form)


# Register bluprints
app.register_blueprint(blog)


# Utils
def create_and_seed_db():
    # Hack for running db commands w/o context
    ctx = app.test_request_context()
    ctx.push()
    db.create_all()
    # Create the administrator role
    user_datastore = app.extensions['security'].datastore
    user_datastore.find_or_create_role(name='admin',
                                       description='Administrator')
    # Create the demo user
    encrypted_password = utils.hash_password('demo')
    user = User(email='demo', password=encrypted_password)
    db.session.add(user)
    db.session.commit()
    user_datastore.add_role_to_user('demo', 'admin')
    db.session.commit()

    return


if __name__ == '__main__':
    # This will create the database if it doesn't already exist.
    if not os.path.exists(
            app.config['SQLALCHEMY_DATABASE_URI'].split('///')[1]):
        create_and_seed_db()
    app.run()
