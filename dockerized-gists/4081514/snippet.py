def watch_variables(var_list):
    """Usage:  @watch_variables(['myvar1', 'myvar2'])"""
    def _decorator(cls):
        def _setattr(self, name, value):
            if name in var_list:
                import traceback
                import sys
                # Print stack (without this __setattr__ call)
                traceback.print_stack(sys._getframe(1))
                print '%s -> %s = %s' % (repr(self), name, value)

            return super(cls, self).__setattr__(name, value)
        cls.__setattr__ = _setattr
        return cls
    return _decorator