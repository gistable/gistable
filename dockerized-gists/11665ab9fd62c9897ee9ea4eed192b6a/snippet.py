# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

class NotMatchingException(Exception):
    pass

"""
This class represente a route 
"""
class Route(object):
    def __init__(self, pattern, action, name=None, verbs=("GET", "HEAD")):        

        self._pattern = str(pattern)
        self._compiledPattern = re.compile(self._pattern)
        self._name = name
        if not callable(action):
            raise TypeError("Argument 'action' must be callable")
        self._action = action

        if type(verbs) is tuple:
            self.verbs = verbs
        elif type(verbs) in [str, unicode]:
            self.verbs = (verbs,)
        else:
            raise TypeError("Argument 'verbs must be tuple or str, %s given" % type(verbs))

    def name(self):
        return self._name

    def pattern(self):
        return self._pattern

    def compiledPattern(self):
        return self._compiledPattern

    def action(self):
        return self._action

    def argumentsFromUri(self, uri):

        if self._compiledPattern.groups == 0:
            return []
        
        args = self._compiledPattern.search(uri).groups()
        return filter(None, args)

"""
This class allows you to group multiple routes used in your application. 
With it you can get an action by a certain uri
"""
class Router(object):
    def __init__(self):
        self._routes = []
        self.autoDelimit = True

    def addRoute(self, route):
        if not type(route) is Route:
            raise TypeError("argument 'route' must be %s" % Route.__name__)
        self._routes.append(route)
        return self

    def filterByUri(self, uri):
        routes = []
        for route in self._routes:
            if re.match(route.pattern(), uri):
                routes.append(route)
        return routes

    def findByUri(self, uri):
        for route in self._routes:
            if route.compiledPattern().match(uri):
                return route
        return None

    def createRoute(self, pattern, action, name=None, verbs=("GET", "HEAD")):

        if self.autoDelimit:
            pattern = r"^/?{0}/?$".format(pattern.strip("/"))

        route = Route(pattern, action, name, verbs)
        self.addRoute(route)
        return route

    def get(self, pattern, action, name=None):
        return self.createRoute(pattern, action, name, ("GET", "HEAD"))

    def post(self, pattern, action, name=None):
        return self.createRoute(pattern, action, name, "POST")

    def put(self, pattern, action, name=None):
        return self.createRoute(pattern, action, name, "PUT")     

    def __call__(self, pattern, name=None, verbs="GET"):
        def addRoute(action):
            return self.createRoute(pattern, action, name, verbs)
        return addRoute

    def callFromUri(self, uri):
        route = self.findByUri(uri)
        if route is None:
            raise NotMatchingException("Route not found")
        args = route.argumentsFromUri(uri)
        return route.action()(*args)


