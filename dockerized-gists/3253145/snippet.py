# Copyright (c) 2012, Erik Youngren <artanis.00@gmail.com>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer. Redistributions in binary
# form must reproduce the above copyright notice, this list of conditions and
# the following disclaimer in the documentation and/or other materials provided
# with the distribution. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""FrozenSet with Axiom of Choice

Usage:

    # Use instead of frozenset
    from FrozenSet import FrozenSet
    s = FrozenSet({'a', 'b', 'c'})
    s.choose()

    # Shadow frozenset with FrozenSet
    from FrozenSet import FrozenSet as frozenset
    s = frozenset({'a', 'b', 'c'})
    s.choose()
    
    # Global monkeypatching (not recommended)
    import FrozenSet
    FrozenSet.patch()
    s = frozenset({'a', 'b', 'c'})
    s.choose()
    FrozenSet.patch.restore()

"""
from unittest import TestCase

try:
    # Python 3
    import builtins
except ImportError:
    # Python 2
    import __builtin__ as builtins

__all__ = ('FrozenSet', )

class FrozenSet(frozenset):
    def choose(self):
        """Picks a single element from the set.

        The exact element returned is left as an implementation detail.

        Raises KeyError if called on an empty set.

        """
        if len(self) > 0:
            return next(iter(self))
        else:
            raise KeyError("Cannot choose from empty set.")

class Monkey:
    """Manages patching and unpatching frozenset.

    It is recommended to simply use FrozenSet on it's own, as monkey
    patching the standard library can result in other code exhibiting
    unexpected behaviour.

    """
    def __call__(self):
        """Replaces default frozenset type with new subclass.

        """
        self.frozenset = builtins.frozenset
        builtins.frozenset = FrozenSet

    def restore(self):
        """Restores default frozenset type.

        """
        builtins.frozenset = self.frozenset

patch = Monkey()

class test_FrozenSet(TestCase):
    def test_zero_len(self):
        s = FrozenSet()
        self.assertRaises(
            KeyError, s.choose)

    def test_choose(self):
        s = FrozenSet({'a', 'b', 'c'})
        self.assertTrue(
            s.choose() in {'a', 'b', 'c'})

class test_Monkey(TestCase):
    def test_patch(self):
        orig_fs = builtins.frozenset
        patch = Monkey()
        patch()
        self.assertEqual(type(FrozenSet), type(frozenset))
        builtins.frozenset = orig_fs

    def test_restore(self):
        patch = Monkey()
        orig_fs = frozenset
        patch()
        patch.restore()
        self.assertEqual(type(frozenset), type(orig_fs))
