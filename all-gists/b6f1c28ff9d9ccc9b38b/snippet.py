from importlib import import_module


# Absolute Imports
# ================

# import <>

import package_A.module_m as m

_package_A = __import__('package_A.module_m')
m = _package_A.module_m

m = import_module('package_A.moduel_m')


# ``from <> import <fromlist>`` statement

from package_A import module_m as m

_package_A = __import__('package_A', fromlist=('module_m',))
m = _package_A.module_m

#_package_A = __import__('package_A')
#_package_A = import_module('package_A')
#m = _package_A.module_m
'''
It would get error as below::
    AttributeError: 'module' object has no attribute 'module_m'
'''

###############################################################################

# Relative Imports
# =================

# import <>

import ..moduel_m as m

m = __import__('module_m', globals=globals(), locals=locals(), level=2)

m = import_module('..module_m', package=__package__)
'''
__package__ == 'package_A.package_B'
'''

# ``from <> import <fromlist>`` statement

from .. import module_m as m

_package_A = __import__('', globals=globals(), locals=locals(), fromlist=('module_m',), level=2)
m = _package_A.module_m

