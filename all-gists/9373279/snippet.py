# -*- coding: utf-8 -*-
# test_docstrings.py
import pytest

def test_lambdas():
    # Create a lambda and test it
    doubler = lambda x: " ".join([x, x])
    assert doubler("fun") == "fun fun"
    
    # Add a docstring to the lambda
    doubler.__doc__ = "Doubles strings"
    
    # Test that calling __doc__ works
    assert doubler.__doc__ == "Doubles strings"
    


# appended to test_docstrings.py
def test_functions():
    # Create a function and test it
    def doubler(x):
        "Doubles strings"
        return " ".join([x, x])
    assert doubler("fun") == "fun fun"
    assert doubler.__doc__ == "Doubles strings"

    # Change the docstring
    doubler.__doc__ = "Really doubles strings"

    # Test that calling __doc__ works
    assert doubler.__doc__ == "Really doubles strings"
    

# more appended to test_docstrings.py
def test_strings():
    # Assert that strings come with a built-in doc string
    s = "Hello, world"
    assert s.__doc__ == 'str(object) -> string\n\nReturn a nice string' \
        ' representation of the object.\nIf the argument is a string,' \
        ' the return value is the same object.'
    
    # Try to set the docstring of a string and you get an AttributeError
    with pytest.raises(AttributeError) as err:
        s.__doc__ = "Stock programming text"
    
    # The error's value explains the problem...
    assert err.value.message == "'str' object attribute '__doc__' is read-only"


# Again appended to test_docstrings.py
def test_subclassed_string():

    # Subclass the string type
    class String(str):
        """I am a string class"""
    
    # Instantiate the string
    s = String("Hello, world")
    
    # The default docstring is set
    assert s.__doc__ == """I am a string class"""
    
    # Let's set the docstring
    s.__doc__ = "I am a string object"
    assert s.__doc__ == "I am a string object"
