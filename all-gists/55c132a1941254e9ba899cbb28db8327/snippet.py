"""Python switch-statement pseudo-implementation
Mimics C-style switch statements
The following code blocks should be equivalent
-----------------------------------------------
switch(arg):
    case 1:
        // Handle case
    case 2:
        // Handle case
    default:
        // Handle default case
-----------------------------------------------
class Case1(SwitchCall):
    def __init__(self, arg1, arg2):
        self.__arg1 = arg1
        self.__arg2 = arg2
    def do_call(self, *args, **kwargs)
        # Handle call
        return self.__arg1 - self.__arg2
class Case2(SwitchCall):
    def __init__(self, arg1, arg2):
        self.__arg1 = arg1
        self.__arg2 = arg2
    def do_call(self, *args, **kwargs)
        # Handle call
        return self.__arg1 * self.__arg2
class CaseDefault(SwitchCall):
    def __init__(self, arg1, arg2):
        self.__arg1 = arg1
        self.__arg2 = arg2
    def do_call(self, *args, **kwargs)
        return self.__arg1 + self.__arg2
switch(arg, {
    case_1 : Case1(arg1, arg2),
    case_2 : Case2(arg1, arg2)
}, CaseDefault(arg1, arg2))
"""
__author__ = 'Thomas Li Fredriksen'
__license__ = 'MIT'

class SwitchCall(object):
    """Switch-call main class
    All switch-call objects must inherit from this class
    """
    def do_call(self, *args, **kwargs):
        """Overload this function to simulate function call"""
        pass
    def __call__(self, *args, **kwargs):
        """Call do_call-method"""
        self.do_call(args, kwargs)
class switch(object):
    def __init__(self, key, cases, default=None):
        """Switch-statement implementation
        :param key: Switch parameter
        :param cases: Dictionary of callbacks
        :param default: Default callback if key is not in cases
        """
        ret = None
        try:
            ret = cases[key]()
        except KeyError:
            if default:
                ret = default()
        finally:
            return ret