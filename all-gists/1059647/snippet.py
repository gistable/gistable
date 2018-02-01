# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
from ndb import model
from webapp2_extends.utils import Unique, UniqueConstraintViolation, \
     check_password_hash, generate_password_hash
from webapp2_extends.auth import create_session_id

DEBUG = True

class User(model.Model):
    """Universal user model. Can be used with App Engine's default users API,
    own auth or third party authentication methods (OpenId, OAuth etc).
    """
    #: Creation date.
    created = model.DateTimeProperty(auto_now_add=True)
    #: Modification date.
    updated = model.DateTimeProperty(auto_now=True)
    #: User defined unique name, also used as key_name.
    username = model.StringProperty(required=True)
    #: Password, only set for own authentication.
    password = model.StringProperty(required=False)
    #: User email
    email = model.StringProperty(required=False)
    # Admin flag.
    is_admin = model.BooleanProperty(default=False)
    #: Authentication identifier according to the auth method in use. Examples:
    #: * own|username
    #: * gae|user_id
    #: * openid|identifier
    #: * twitter|username
    #: * facebook|username
    auth_id = model.StringProperty(repeated=True)
    # Flag to persist the auth across sessions for third party auth.
    auth_remember = model.BooleanProperty(default=False)
    # Auth token, renewed periodically for improved security.
    session_id = model.StringProperty(required=True)
    # Auth token last renewal date.
    session_updated = model.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_by_username(cls, username):
        return cls.query(cls.username == username).get()

    @classmethod
    def get_by_auth_id(cls, auth_id):
        return cls.query(cls.auth_id == auth_id).get()

    @classmethod
    def create(cls, username, auth_id, **kwargs):
        """Creates a new user and returns it. If the username already exists,
        returns None.

        :param username:
            Unique username.
        :param auth_id:
            Authentication id, according the the authentication method used.
        :param email:
            Unique email address.
        :param kwargs:
            Additional entity attributes.
        :returns:
            The newly created user or None if the username already exists.
        """
        # Assemble the unique scope/value combinations.
        unique_username = 'User.username:%s' % username
        unique_auth_id = 'User.auth_id:%s' % auth_id
        # Create the unique username, auth_id and email.
        uniques = [unique_username, unique_auth_id]
        # TODO add email to parms in tipfy.auth so that
        # we don't have to use kwargs here
        if 'email' in kwargs:
            unique_email = 'User.email:%s' % kwargs['email']
            uniques.append(unique_email)

        success, existing = Unique.create_multi(uniques)

        if success or DEBUG:
            kwargs['username'] = username
            # make this a list so that we can have multiple auth methods.
            kwargs['auth_id'] = [auth_id]
            # Generate an initial session id.
            kwargs['session_id'] = create_session_id()
            if 'password_hash' in kwargs:
                # Password is already hashed.
                kwargs['password'] = kwargs.pop('password_hash')
            elif 'password' in kwargs:
                # Password is not hashed: generate a hash.
                kwargs['password'] = generate_password_hash(kwargs['password'])
            user = cls(**kwargs)
            user.put()
            return user
        else:
            # The ordering her is important. Email must come before
            # auth id or the error return will make little since to the user.
            if unique_email in existing:
                raise UniqueConstraintViolation('Email %s already '
                                                'exists. Try logging in.' % kwargs['email'])
            if unique_username in existing:
                raise UniqueConstraintViolation('Username %s already '
                    'exists' % username)

            if unique_auth_id in existing:
                raise UniqueConstraintViolation('Auth id %s already '
                                                'exists' % auth_id)

    def set_password(self, new_password):
        """Sets a new, plain password.

        :param new_password:
            A plain, not yet hashed password.
        :returns:
            None.
        """
        self.password = generate_password_hash(new_password)

    def check_password(self, password):
        """Checks if a password is valid. This is done with form login

        :param password:
            Password to be checked.
        :returns:
            True is the password is valid, False otherwise.
        """
        if check_password_hash(self.password, password):
            return True

        return False

    def check_session(self, session_id):
        """Checks if an auth token is valid.

        :param session_id:
            Token to be checked.
        :returns:
            True is the token id is valid, False otherwise.
        """
        if self.session_id == session_id:
            return True

        return False

    def renew_session(self, force=False, max_age=None):
        """Renews the session id if its expiration time has passed.

        :param force:
            True to force the session id to be renewed, False to check
            if the expiration time has passed.
        :returns:
            None.
        """
        if not force:
            # Only renew the session id if it is too old.
            expires = datetime.timedelta(seconds=max_age)
            force = (self.session_updated + expires < datetime.datetime.now())

        if force:
            self.session_id = create_session_id()
            self.session_updated = datetime.datetime.now()
            self.put()

    def __unicode__(self):
        """Returns this entity's username.

        :returns:
            Username, as unicode.
        """
        return unicode(self.username)

    def __str__(self):
        """Returns this entity's username.

        :returns:
            Username, as unicode.
        """
        return self.__unicode__()

    def __eq__(self, obj):
        """Compares this user entity with another one.

        :returns:
            True if both entities have same key, False otherwise.
        """
        if not obj:
            return False

        return str(self.key) == str(obj.key)

    def __ne__(self, obj):
        """Compares this user entity with another one.

        :returns:
            True if both entities don't have same key, False otherwise.
        """
        return not self.__eq__(obj)