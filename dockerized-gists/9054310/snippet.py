# the following is a basically functional but probably broken for some cases (just tested for basic login ATM) implementation of a flask-security UserDataStore for RethinkDB.
#
# This is released as open source under the MIT license and comes with no warranty, yada yada. TODO: actual license header
from flask_security import UserMixin, RoleMixin
from flask_security.datastore import UserDatastore
import rethinkdb as r

class Bunch(object):
    def __init__(self, obj, **kws):
        self.__dict__.update(obj)
        self.__dict__.update(kws)

    def __repr__(self):
        return 'Bunch({})'.format(repr(self.__dict__))


class User(Bunch, UserMixin):
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        if not hasattr(self, 'active'):
            self.active = True

        if not hasattr(self, 'roles'):
            self.roles = []


class Role(Bunch, RoleMixin):
    def __init__(self, *args, **kwargs):
        super(Role, self).__init__(*args, **kwargs)


class RethinkDBUserDatastore(UserDatastore):
    def __init__(self, db, user_table='users', role_table='roles', user_pk='id', role_pk='name'):
        self.db = db
        self.user_table = user_table
        self.role_table = role_table
        self.user_pk = user_pk
        self.role_pk = role_pk

    def commit(self):
        pass

    def get_user(self, id_or_email):
        if '@' in id_or_email:
            obj = r.table(self.user_table).get_all(id_or_email, index='email')[0].run(self.db.conn)
        else:
            obj = r.table(self.user_table).get(id_or_email).run(self.db.conn)

        return User(obj)

    def find_user(self, **query):
        return User(r.table(self.user_table).filter(query)[0].run(self.db.conn))

    def find_role(self, **query):
        return Role(r.table(self.role_table).filter(query)[0].run(self.db.conn))

    def add_role_to_user(self, user, role):
        return r.table(self.user_table) \
                .get(user[self.user_pk]) \
                .update({'roles': r.row['roles'].default([]).set_insert(role.name)}) \
                .run(self.db.conn)

    def remove_role_from_user(self, user, role):
        return r.table(self.user_table) \
                .get(user[self.user_pk]) \
                .update({'roles': r.row['roles'].default([]).set_difference([role.name])}) \
                .run(self.db.conn)

    def toggle_active(self, user):
        user['active'] = not user.get('active', True)
        return True

    def deactivate_user(self, user):
        active = user.get('active', True)
        if active:
            user['active'] = False
            return True
        return False

    def activate_user(self, user):
        active = user.get('active', True)
        if not active:
            user['active'] = True
            return True
        return False

    def create_role(self, **role):
        result = r.table(self.role_table).insert(role, return_vals=True).run(self.db.conn)
        return result['new_val']

    def create_user(self, **user):
        if 'roles' in user:
            user['roles'] = [role['name'] for role in roles]

        result = r.table(self.user_table).insert(user, return_vals=True).run(self.db.conn)
        return result['new_val']

    def delete_user(self, user):
        r.table(self.user_table).get(user[self.user_pk]).delete().run(self.db.conn)