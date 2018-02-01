#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 The Octopus Apps Inc.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# Author: Alejandro M. Bernardis
# Email: alejandro.m.bernardis at gmail.com
# Created: Feb 6, 2012, 2:44:12 PM
#

import functools
import urllib
import urlparse

from tornado.escape import json_decode, json_encode
from tornado.web import RequestHandler, HTTPError

#: -- helpers ------------------------------------------------------------------

__all__ = ["BaseHandler", 
           "AuthBaseHandler",
           "Role",
           "authenticated_plus",
           "roles",]

#: -- BaseHandler --------------------------------------------------------------

class BaseHandler(RequestHandler):
    
    #: helpers
    
    def get_arguments_list(self, args=[]):
        result = dict()
        for k in args:
            v = self.get_argument(k, None)
            result[k] = None if not v else v
        return result
    
    def get_json_response(self, error_id=0, error_message=None, response=None):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        result = dict(error=dict(id=error_id, message=error_message), 
                      response=response)
        return json_decode(json_encode(result))
    
    #: properties
    
    @property
    def next_url(self):
        return self.get_argument("next", None)
    
    #: methods
    
    def do_next_or_root(self):
        self.redirect(self.next_url or "/")
        
    def do_root(self):
        self.redirect("/")

#: -- AuthBaseHandler ----------------------------------------------------------

class AuthBaseHandler(BaseHandler):
    
    #: helpers
    
    def get_user_value(self, key=None):
        if not self.current_user or not key: 
            return None
        value = key.split(".")
        v = self.current_user.get(value[0])
        if not v: 
            return None
        value = value[1:]
        for k in range(len(value)):
            v = v.get(value[k])
            if not v and k < len(value):
                return None
        return v
    
    def get_current_user(self):
        user = self.get_secure_cookie(self.settings["cookie_user_session"])
        if not user or user is "":
            return None
        return json_decode(user)
    
    def set_current_user(self, user=None, remember_me=False):
        user_data = "" if not user else json_encode(user.to_object())
        user_remember = 1 if not remember_me else 365
        self.set_secure_cookie(self.settings["cookie_user_session"], 
                               user_data,
                               user_remember)
    
    #: properties
    
    @property
    def is_admin(self):
        return self.role.is_admin
    
    @property
    def role(self):
        role = self.get_user_value("role")
        return role
        
    @property
    def role_name(self):
        role = self.role
        return None if not role else role.name

#: -- roles --------------------------------------------------------------------

class Role(object):
    #: perms

    __perms_read  = 1 << 0
    __perms_write = 1 << 16
    __perms_admin = 1 << 32

    #: methods

    def __init__(self, name, write=False, admin=False):

        if not hasattr(Role, "_roles"):
            Role._roles = dict()

        self._name = name
        self._perms = self.__perms_read

        if write:
            self._perms = self._perms\
                        | self.__perms_write

        if admin:
            self._perms = self._perms\
                        | self.__perms_write\
                        | self.__perms_admin

        if not Role._roles.has_key(name):
            Role._roles[name] = self

    @property
    def name(self):
        return self._name if hasattr(self, "_name") else None

    @property
    def permissions(self):
        return self._perms if hasattr(self, "_perms") else -1

    @property
    def is_admin(self):
        return self.permissions >= self.__perms_admin

    @property
    def is_writer(self):
        return self.permissions >= self.__perms_write

    @property
    def is_reader(self):
        return self.permissions >= self.__perms_read

    @staticmethod
    def get_role(key=None):
        if key and Role._roles.has_key(key):
            return Role._roles.get(key)
        return None

    @staticmethod
    def get_role_by_value(rid=None):
        if rid and Role._roles:
            for r in Role._roles.items():
                if r[1].permissions == rid:
                    return r[1]
        return None

    @staticmethod
    def get_admin_value():
        return Role.__perms_admin

    @staticmethod
    def get_writer_value():
        return Role.__perms_write

    @staticmethod
    def get_reader_value():
        return Role.__perms_read

#: -- wrappers -----------------------------------------------------------------

def authenticated_plus(*roles):
    def wrap(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.current_user:
                if not self.request.method in ("GET", "HEAD"):
                    raise HTTPError(403)
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urllib.urlencode(dict(next=next_url))
                self.redirect(url)
                return
            user = self.get_user_value("role")
            perms = Role.get_name_role(user).name
            if not perms in roles:
                raise HTTPError(403)
            return method(self, *args, **kwargs)
        return wrapper
    return wrap

def roles(*roles):
    def wrap(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.current_user:
                user = self.get_user_value("role")
                perms = Role.get_name_role(user).name
                if perms in roles:
                    return method(self, *args, **kwargs)
            raise HTTPError(403)
        return wrapper
    return wrap