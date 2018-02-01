"""
Copyright (c) 2012 Anthony Wu, twitter.com/anthonywu

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

class EnumException(Exception):
    """A configuration or attribute access exception in HumanEnums"""
    pass

class EnumStr(str):
    """A string with a readable human-friendly value."""
    @property
    def human(self):
        return self._human
    @human.setter
    def human(self, h):
        self._human = h

class HumanEnums(object):
    """
    A human-friendly Enum object maker that makes easy:
      1. Declaring storage value and display value together
      2. Accessing the display value of an enum value
      3. Accessing the name and value sets

    >>> from human_enum import HumanEnums
    >>> WorkflowStatus = HumanEnums(
    ...     NEW = ('N', 'New'),
    ...     PENDING = ('P', 'Pending'),
    ...     DONE = ('D', 'Done'),
    ...     CANCELED = ('C', 'Canceled')
    ...     )
    >>> 
    >>> WorkflowStatus.names
    set(['CANCELED', 'DONE', 'PENDING', 'NEW'])
    >>> WorkflowStatus.values
    set(['P', 'C', 'D', 'N'])
    >>> WorkflowStatus.NEW
    'N'
    >>> str(WorkflowStatus.NEW)
    'N'
    >>> WorkflowStatus.NEW.human
    'New'
    >>> WorkflowStatus.NON_EXISTING
      ...
    human_enum.EnumException: Enum value NON_EXISTING is not defined    
    """
    def __init__(self, **enum_args):
        self._name_set = set(enum_args.keys())
        self._val_set = set()
        self._enums = []
        for name, (val, human_val) in enum_args.iteritems():
            self._val_set.add(val)
            v = EnumStr(val)
            v.human = human_val
            setattr(self, name, v)
            self._enums.append(v)
        if len(self._val_set) != len(enum_args):
            raise EnumException("Duplicate values found in enum declarations")

    @property
    def names(self):
        return self._name_set

    @property
    def values(self):
        return self._val_set

    @property
    def val_to_human_map(self):
        return dict((e, e.human) for e in self._enums)

    def __getattr__(self, name):
        raise EnumException("Enum value %s is not defined" % name)
