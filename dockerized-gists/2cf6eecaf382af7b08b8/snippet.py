#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playing Around with the Command Bus Pattern in Python
"""

import inspect
import collections


class HandlerNotFound(Exception):
    pass


class Resolver:

    def handler_for(self, command):
        """
        Retrieve the handler class for a command. If the command implements a
        ``handler`` method, it should return the class of the handler. Otherwise
        it will search for a class with the name {CommandName}Handler.
        """
        try:
            return command.handler()
        except AttributeError:
            pass

        try:
            return getattr(self._getmodule(command), command.__class__.__name__+'Handler')
        except AttributeError:
            return None

    def validator_for(self, command):
        """
        Retrieve the validator class for a command. If the command implements a
        ``validator`` method, it should return the class of the handler. Otherwise
        it will search for a class with the name {CommandName}Validator.
        """
        try:
            return command.validator()
        except AttributeError:
            pass

        try:
            return getattr(self._getmodule(command), command.__class__.__name__+'Validator')
        except AttributeError:
            return None

    def _getmodule(self, command):
        return inspect.getmodule(command)


class Bus:
    """
    The actual command bus, when given a command, it finds an appropriate handler
    and fires it.
    """

    #: The command name resolver, used to figure out names for commands that
    #: don't have a `handler` method.
    resolver = None

    def __init__(self, resolver=None):
        self.resolver = resolver or Resolver()

    def execute(self, command):
        validator_cls = self.resolver.validator_for(command)
        if validator_cls is not None:
            validator_cls().validate(command)

        handler_cls = self.resolver.handler_for(command)
        if handler_cls is None:
            raise HandlerNotFound('Unable to find handler for '+command.__class__.__name__)
        return handler_cls().handle(command)


SayHelloCommand = collections.namedtuple('SayHelloCommand', 'name')


class SayHelloCommandHandler:

    def handle(self, command):
        print("Hello, "+command.name)


class SayHelloCommandValidator:

    def validate(self, command):
        print(command.__class__.__name__, 'seems normal')
        return True


class SayGoodbyeCommand(collections.namedtuple('SayGoodbyeCommand', 'name')):

    def handler(self):
        return GoodbyeHandler

    def validator(self):
        return GoodbyeValidator


class GoodbyeHandler:

    def handle(self, command):
        print("Goodbye, "+command.name)


class GoodbyeValidator:

    def validate(self, command):
        print(command.__class__.__name__, 'seems okay')


SayGoodnightCommand = collections.namedtuple('SayGoodnightCommand', 'name')


class SayGoodnightCommandHandler:

    def handle(self, command):
        print('Goodnight, '+command.name)


NoHandlerCommand = collections.namedtuple('NoHandlerCommand', 'name')


if __name__ == '__main__':
    bus = Bus()
    bus.execute(SayHelloCommand('world'))
    bus.execute(SayGoodbyeCommand('world'))
    bus.execute(SayGoodnightCommand('moon'))
    try:
        bus.execute(NoHandlerCommand('nope'))
    except HandlerNotFound:
        print("No handler found!")