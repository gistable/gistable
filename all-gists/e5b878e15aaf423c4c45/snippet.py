# -*- coding: utf-8 -*-

# functions_core.py
# Elements:
#       [X] IRC exceptions
#       [X] sandbox function
#       [X] function object

import core

class IRCException(Exception):
	pass

class InvalidPasswordException(IRCException):
        pass
class NotSufficentPrivilegesException(IRCException):
        pass
class MutedCommandException(IRCException):
        pass
class MutedUserException(IRCException):
        pass
class UnknownCommandException(IRCException):
        pass
class InvalidArgumentsException(IRCException):
        pass

class _function_return:
        def __eq__(self, c):
                return isinstance(self, c)
        
class NEXT(_function_return):
        """ sent by a function when it terminates """

class STOP(_function_return):
        """ sent by a function when it terminates """
        def __init__(self, data):
                """ to_send could be either a core.ToSend object either None """
                self.data = data

# a function either sends NEXT to call the next function on the list either
# STOP, with argument what should be printed back on the channel, sent to a
# print_to_channel type of function

def Sandbox(func):
        def f(*args, **kwargs):
                print('beggining of execution...\n\tsandboxing func...')
                try:
                        ret = func(*args, **kwargs)
                except IRCException as e:
                        print('\tERROR:', e)
                else:
                        print('\texecution went fine.')
                        if ret == STOP:
                                print('\tfunction requested STOP:')
                                print('\t\t"', ret.data.content, '" to be sent to ', ret.data.target, sep='')
                        elif ret == NEXT:
                                print('\tfunction requested NEXT')
                finally:
                        print('end of execution.')
        return f

class _Function:
        def __init__(self, cmdnames, f, priority):
                self.f = f
                self.cmdnames = cmdnames
                self.priority = priority
                self.muted = False
                self.muted_users = []
        def __call__(self, *args, **kwargs):
                return self.f(*args, **kwargs)

def Function(cmdnames, priority):
        def decorator(f):
                return _Function(cmdnames, f, priority)
        return decorator

@Sandbox
@Function(cmdnames=('reverse',), priority=1)
def reverse(s):
        return STOP(core.ToSend('#bite', s[::-1]))
