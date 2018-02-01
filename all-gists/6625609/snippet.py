from flask import Flask, request, abort, g, current_app

from flask.ext.principal import Principal
from flask.ext.principal import Identity, identity_changed, identity_loaded
from flask.ext.principal import Permission, Need, RoleNeed, ItemNeed

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'
app.config['TESTING'] = True

Principal(app)

admin = Permission(RoleNeed('admin'))
manager_or_blogger = Permission(RoleNeed('manager'), RoleNeed('blogger'))
blogger = Permission(RoleNeed('blogger'))

@identity_loaded.connect
def _on_principal_init(sender, identity):
    # Standard, not lazy roles
    role_map = {
        'admin': (RoleNeed('admin'),),
        'manager': (RoleNeed('manager'),),
        'blogger': (RoleNeed('blogger'),),
        'admin_blogger': (RoleNeed('admin'), RoleNeed('blogger')),
        'manager_blogger': (RoleNeed('manager'), RoleNeed('blogger')),
    }

    roles = role_map.get(identity.id)
    if roles:
        for role in roles:
            identity.provides.add(role)


class Blog(object):
    def __init__(self, identity, title):
        self.identity = identity
        self.title = title
blogs = {}


class BlogEntryEditPermission(Permission):
    """
    Lazily loaded permission check.
    """

    def allows(self, identity):
        # current entry is already in the request
        blog_id = request.view_args.get('blog_id')
        blog = blogs.get(blog_id)
        if not blog:
            # free sanity check.
            abort(404)

        result = blog.identity == identity.id
        return result

blog_edit = BlogEntryEditPermission()


@app.route('/')
def hello():
    return 'Hello %s!' % g.identity.id

@app.route('/login/<userid>')
def login_admin(userid):
    identity_changed.send(current_app._get_current_object(),
                          identity=Identity(userid))
    return 'logged in as %s' % userid

@app.route('/logout')
def logout():
    identity_changed.send(current_app._get_current_object(),
                          identity=Identity(None))
    return 'logged out'

@app.route('/blog/create', methods=['GET', 'POST'])
@blogger.require()
def blog_create():
    if request.method == 'POST':
        blog = Blog(g.identity.id, 'blog title')
        blog.id = len(blogs) + 1
        blogs[blog.id] = blog
        return 'Blog entry %s created' % blog.id
    return ('<form method="POST"><p>Create your blog entry.</p>'
        '<input type="submit"/></form>')

@app.route('/blog/edit/<int:blog_id>')
@blogger.require()
@blog_edit.require()
def blog_edit(blog_id):
    return 'Editing blog entry: %s' % blog_id
    # XXX question: how do you let manager blogger be able to edit all
    # entries?

@app.route('/blog/manage')
@manager_or_blogger.require()
def blog_manage():
    # Only managers or bloggers can view this.
    return 'Restricted Blog management Tool.'

@app.route('/blog/admin')
@admin.require()
@manager_or_blogger.require()
def blogadmin():
    # Only admins who are also managers or bloggers can view this.
    return 'Blog Administrative Tool.'

if __name__ == '__main__':
    app.run(port=8880)
