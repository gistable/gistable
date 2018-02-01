# -*- coding: utf-8 -*-
# In order to run this script, you'll need to 
#   have both py.test and six installed. 
#   Assuming you have pip, in a virtualenv just
#   type at the command-line:
#       
#       pip install pytest six
#
# To run it, just type:
#
#       python test_fun_with_partials.py

def power(base, exponent):
    return base ** exponent


def square(base):
    return power(base, 2)
    
def cube(base):
    return power(base, 3)
    

from functools import partial

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

def test_partials():
    assert square(2) == 4
    assert cube(2) == 8
    

def test_partial_docs():
    assert square.keywords == {"exponent": 2}
    assert square.func == power

    assert cube.keywords == {"exponent": 3}
    assert cube.func == power


def test_power_partials():

    # List to store the partials
    power_partials = []
    for x in range(1, 11):

        # create the partial
        f = partial(power, exponent=x)
        
        # Add the partial to the list
        power_partials.append(f)

    # We could just use list comprehension instead of the loop
    # [partial(power, exponent=x) for x in range(1, 11)]
    
    
    # Test the first power
    assert power_partials[0](2) == 2
    
    # Test the fifth power
    assert power_partials[4](2) == 32
    
    # Test the tenth power
    assert power_partials[9](2) == 1024        



# Since I like my article code to work in both Python 2.7 and 3,
#   I'll import the excellent six library to manage the
#   differences between Python versions. Six is available on PyPI
#   at https://pypi.python.org/pypi/six.
from six import add_metaclass 

class PowerMeta(type):
    def __init__(cls, name, bases, dct):
    
        # generate 50 partial power functions:
        for x in range(1, 51):
        
            # Set the partials to the class
            setattr(
                # cls represents the class
                cls,
                
                # name the partial
                "p{}".format(x),
                
                # partials created here
                partial(power, exponent=x)
            )
        super(PowerMeta, cls).__init__(name, bases, dct)

@add_metaclass(PowerMeta)
class PowerStructure(object):
    pass

def test_power_structure_object():
    p = PowerStructure()

    # 10 squared
    assert p.p2(10) == 100
    
    # 2 to the 5th power
    assert p.p5(2) == 32

    # 2 to the 50th power
    assert p.p50(2) == 1125899906842624

def test_power_structure_class():
    # Thanks to the power of metaclasses, we don't need to instantiate!
    
    # 10 squared
    assert PowerStructure.p2(10) == 100
    
    # 2 to the 5th power
    assert PowerStructure.p5(2) == 32

    # 2 to the 50th power
    assert PowerStructure.p50(2) == 1125899906842624
        
        
if __name__ == "__main__":
    import pytest
    pytest.main()